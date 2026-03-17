from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import enum

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

class Role(str, enum.Enum):
    CAREGIVER = "CAREGIVER"
    ELDER = "ELDER"

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[Role] = None
    full_name: Optional[str] = None
    elder_id: Optional[str] = None

blacklisted_tokens = set()

def get_password_hash(password: str) -> str:
    # bcrypt has a 72 byte limit — truncate safely
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password[:72], hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    if token in blacklisted_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been blacklisted",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        role_str: str = payload.get("role")
        full_name: str = payload.get("full_name")
        elder_id: str = payload.get("elder_id")
        
        if username is None or role_str is None:
            raise credentials_exception
        try:
            role = Role(role_str)
        except ValueError:
            raise credentials_exception
        token_data = TokenData(username=username, role=role, full_name=full_name, elder_id=elder_id)
    except JWTError:
        raise credentials_exception
    return token_data

def require_role(required_role: Role):
    async def role_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Requires {required_role.value} role."
            )
        return current_user
    return role_checker

def verify_elder_self_access(elder_id: str, current_user: TokenData):
    if current_user.role == Role.CAREGIVER:
        return True
    if current_user.role == Role.ELDER and current_user.username == elder_id:
        return True
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied. Elders can only access their own data."
    )
