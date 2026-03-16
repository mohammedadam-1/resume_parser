from fastapi import APIRouter, HTTPException
from src.db.user_auth import UserAuth
from pydantic import BaseModel

router = APIRouter()

auth = UserAuth()

class UserSchema(BaseModel):
    email: str
    password: str

@router.post("/signup")
def signup(user: UserSchema):
    response = auth.user_signup(user.email, user.password)
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return {"message": "Signup successfull", "user":response.user}

@router.post("/login")
def signin(user: UserSchema):
    response = auth.user_signin(user.email, user.password)
    if response.error:
        raise HTTPException(status_code=401, detail=response.error.message)
    return {"session": response.session}

