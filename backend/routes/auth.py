from fastapi import APIRouter, HTTPException, Depends, status, Header
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Optional
import json
import os
from google.oauth2 import id_token
from google.auth.transport import requests

from database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "super-secret-compiler-key-123" # In production, use env var
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleAuth(BaseModel):
    token: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = c.fetchone()
        conn.close()
        
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return dict(user)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

def get_current_user_optional(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = c.fetchone()
        conn.close()
        return dict(user) if user else None
    except jwt.PyJWTError:
        return None

@router.post("/register", response_model=Token)
async def register(user_data: UserRegister):
    conn = get_db()
    c = conn.cursor()
    
    # Check if email exists
    c.execute("SELECT id FROM users WHERE email = %s", (user_data.email,))
    if c.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user_data.password)
    default_settings = json.dumps({
        "model": "gemini",
        "runtimeMode": "simulation",
        "exportJson": True,
        "exportValidation": True,
        "exportEvaluation": False,
        "autoRepair": True,
        "showPipelineAnimations": True,
        "defaultTab": "overview"
    })
    
    c.execute(
        "INSERT INTO users (name, email, password_hash, settings_json) VALUES (%s, %s, %s, %s) RETURNING id",
        (user_data.name, user_data.email, hashed_password, default_settings)
    )
    user_id = c.fetchone()['id']
    conn.commit()
    conn.close()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user_id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {"name": user_data.name, "email": user_data.email, "settings": json.loads(default_settings)}
    }

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = %s", (user_data.email,))
    user = c.fetchone()
    conn.close()
    
    if not user or not pwd_context.verify(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["id"])}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "name": user["name"], 
            "email": user["email"], 
            "settings": json.loads(user["settings_json"])
        }
    }

@router.post("/google", response_model=Token)
async def google_auth(auth_data: GoogleAuth):
    """Authenticate with a Google OAuth access token (implicit flow).
    
    Fetches user info from Google, creates the user if they don't exist,
    and returns our standard JWT.
    """
    import httpx
    
    try:
        # Use the access token to get user info from Google
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {auth_data.token}"}
            )
        
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid Google access token")
        
        userinfo = resp.json()
        email = userinfo.get("email")
        name = userinfo.get("name", email.split("@")[0] if email else "User")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")
            
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = c.fetchone()
        
        if not user:
            # Auto-register OAuth users with an unguessable password
            import secrets
            random_password = secrets.token_urlsafe(16)
            hashed_password = pwd_context.hash(random_password)
            default_settings = json.dumps({
                "model": "gemini",
                "runtimeMode": "simulation",
                "exportJson": True,
                "exportValidation": True,
                "exportEvaluation": False,
                "autoRepair": True,
                "showPipelineAnimations": True,
                "defaultTab": "overview"
            })
            c.execute(
                "INSERT INTO users (name, email, password_hash, settings_json) VALUES (%s, %s, %s, %s) RETURNING id",
                (name, email, hashed_password, default_settings)
            )
            user_id = c.fetchone()['id']
            conn.commit()
            
            c.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = c.fetchone()
            
        conn.close()
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user["id"])}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user": {
                "name": user["name"], 
                "email": user["email"], 
                "settings": json.loads(user["settings_json"])
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Google authentication failed: {str(e)}")

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "name": current_user["name"],
        "email": current_user["email"],
        "settings": json.loads(current_user["settings_json"])
    }
