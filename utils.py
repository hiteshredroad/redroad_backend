from fastapi import Depends, HTTPException, Security, Cookie, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from bson import ObjectId
from decouple import config
from typing import Optional, Union, List
from functools import wraps
from datetime import datetime, timedelta, timezone
from database import session as sdb


session_collection = sdb.get_collection("sessions")

SECRET_KEY = config('SECRET_KEY')
LIMIT = int(config('LIMIT', 2))
ALGORITHM = config('ALGORITHM', default="HS256")
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    session = await session_collection.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Session not found")

    if session["expires_at"] < datetime.utcnow():
        await session_collection.delete_one({"session_id": session_id})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    await session_collection.update_one(
        {"session_id": session_id},
        {"$set": {"expires_at": datetime.now(
            timezone.utc) + timedelta(minutes=30)}}
    )

    return session


# check role in api endpoint
def check_roles(required_roles: List[str]):
    def decorator(func):
        # for preserve metadata
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=401, detail="User not authenticated")

            user_roles = current_user.get('roles', [])
            if not any(role in required_roles for role in user_roles):
                raise HTTPException(
                    status_code=403, detail="User does not have the required role")

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def convert_objectid_to_str(document):
    for key, value in document.items():
        if isinstance(value, ObjectId):
            document[key] = str(value)
        elif isinstance(value, dict):
            convert_objectid_to_str(value)
    return document


def get_skip_and_limit(page):
    if page < 1:
        raise HTTPException(
            status_code=400, detail="Page number must be greater than or equal to 1")
    skip = (page - 1) * LIMIT
    return [skip, LIMIT]
