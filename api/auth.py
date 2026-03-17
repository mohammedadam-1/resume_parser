# auth.py
from fastapi import APIRouter, HTTPException
from src.db.user_auth import UserAuth
from pydantic import BaseModel, field_validator



router = APIRouter(prefix="/auth")
auth = UserAuth()

class UserSchema(BaseModel):
    email: str
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

@router.post("/signup", status_code=201)
def signup(user: UserSchema):
    try:
        response = auth.user_signup(user.email, user.password)
        return {"message": "Signup successful", "user": response.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(user: UserSchema):
    try:
        response = auth.user_signin(user.email, user.password)
        
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer"
        }   
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {str(e)}")
    
class RefreshSchema(BaseModel):
    refresh_token: str

@router.post("/refresh")
def refresh(body: RefreshSchema):
    try:
        response = auth.supabase.auth.refresh_session(body.refresh_token)
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Could not refresh session: {str(e)}")    