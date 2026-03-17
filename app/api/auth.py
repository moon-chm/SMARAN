from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import (
    create_access_token, 
    verify_password, 
    get_password_hash, 
    Role, 
    get_current_user, 
    TokenData, 
    blacklisted_tokens, 
    oauth2_scheme
)
from app.graph.connection import neo4j_manager
from app.graph.queries import (
    GET_USER_BY_USERNAME, 
    GET_USER_BY_EMAIL, 
    CREATE_USER, 
    ENSURE_ELDER_NODE
)
from pydantic import BaseModel
import re
from datetime import datetime

router = APIRouter(prefix="/api/auth", tags=["auth"])

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    role: Role

@router.post("/register")
async def register(user_data: UserRegister):
    # Validate password
    if len(user_data.password) < 8 or not re.search(r"\d", user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long and contain at least one number"
        )
    
    async with await neo4j_manager.get_session("system") as session:
        # Check for duplicate username
        res_username = await session.run(GET_USER_BY_USERNAME, {"username": user_data.username})
        if await res_username.single():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
            
        # Check for duplicate email
        res_email = await session.run(GET_USER_BY_EMAIL, {"email": user_data.email})
        if await res_email.single():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
            
        # Prepare parameters
        password_hash = get_password_hash(user_data.password)
        elder_id = user_data.username if user_data.role == Role.ELDER else None
        now_str = datetime.utcnow().isoformat()
        
        # Create user node
        params = {
            "username": user_data.username,
            "email": user_data.email,
            "password_hash": password_hash,
            "role": user_data.role.value,
            "elder_id": elder_id,
            "full_name": user_data.full_name,
            "created_at": now_str,
            "is_active": True
        }
        await session.run(CREATE_USER, params)
        
        # If elder, merge elder node
        if user_data.role == Role.ELDER:
            await session.run(ENSURE_ELDER_NODE, {
                "elder_id": elder_id,
                "full_name": user_data.full_name,
                "created_at": now_str
            })
            
    return {"message": "User registered successfully"}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    async with await neo4j_manager.get_session("system") as session:
        res = await session.run(GET_USER_BY_USERNAME, {"username": form_data.username})
        record = await res.single()
        
    if not record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = record["u"]
    if not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(
        data={
            "sub": user["username"],
            "role": user["role"],
            "full_name": user.get("full_name"),
            "elder_id": user.get("elder_id")
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def get_me(current_user: TokenData = Depends(get_current_user)):
    return current_user

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    blacklisted_tokens.add(token)
    return {"message": "Successfully logged out"}
