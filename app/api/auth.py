from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, verify_password, Role

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Hardcoded demo users for the prototype phase
DEMO_USERS = {
    "caregiver_demo": {
        "password": "password123", # In normal flow this would be hashed in DB
        "role": Role.CAREGIVER
    },
    "elder_123": {
        "password": "password123",
        "role": Role.ELDER
    }
}

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = DEMO_USERS.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(
        data={"sub": form_data.username, "role": user["role"].value}
    )
    return {"access_token": access_token, "token_type": "bearer"}
