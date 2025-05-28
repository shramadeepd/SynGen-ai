from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
from typing import Dict, Any, Optional, List

# Load JWT secret from environment variable, with a default for development
SECRET = os.getenv("JWT_SECRET", "dev_secret_change_in_production")
ALGO = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
security = HTTPBearer()

class TokenData(BaseModel):
    username: str
    role: str
    region: Optional[str] = None
    permissions: List[str] = []
    exp: Optional[datetime] = None

def create_access_token(data: Dict[str, Any], expires_delta: timedelta = None) -> str:
    """
    Create a new JWT access token
    
    Args:
        data: Payload data to include in the token
        expires_delta: Optional expiration time
        
    Returns:
        Encoded JWT string
    """
    to_encode = data.copy()
    
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGO)
    
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token
    
    Args:
        token: The JWT token string
        
    Returns:
        Decoded payload as a dictionary
        
    Raises:
        JWTError: If token is invalid or expired
    """
    return jwt.decode(token, SECRET, algorithms=[ALGO])

def current_user(creds: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Dependency to extract and validate the current user from a JWT token
    
    Args:
        creds: HTTP Authorization credentials containing the JWT
        
    Returns:
        Decoded user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(creds.credentials, SECRET, algorithms=[ALGO])
        
        # Check if token is expired
        if "exp" in payload and datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return payload  # dict with "username", "role", "region", "permissions", etc.
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def role_required(allowed_roles: List[str]):
    """
    Dependency factory to require specific roles for an endpoint
    
    Args:
        allowed_roles: List of role names that can access the endpoint
        
    Returns:
        Dependency function that validates user roles
    """
    def role_checker(user: Dict[str, Any] = Depends(current_user)) -> Dict[str, Any]:
        if user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {user.get('role')} not authorized to access this resource"
            )
        return user
    
    return role_checker

def has_permission(required_permission: str):
    """
    Dependency factory to require specific permissions for an endpoint
    
    Args:
        required_permission: Permission name that is required
        
    Returns:
        Dependency function that validates user permissions
    """
    def permission_checker(user: Dict[str, Any] = Depends(current_user)) -> Dict[str, Any]:
        user_permissions = user.get("permissions", [])
        
        if required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_permission}' is required"
            )
        return user
    
    return permission_checker

def get_current_user_for_db():
    """
    Return a function that sets up Postgres RLS based on the current user
    
    This is used with asyncpg to set session variables for row-level security
    """
    async def setup_db_context(conn, user):
        # Set session variables that Postgres RLS policies can use
        await conn.execute(f"SET app.user_id = '{user.get('sub')}'")
        await conn.execute(f"SET app.role = '{user.get('role')}'")
        await conn.execute(f"SET app.region = '{user.get('region', 'global')}'")
        
    return setup_db_context
