import os
from datetime import timedelta, datetime, timezone
from typing import Annotated

import bcrypt
import inject
import jwt
from fastapi import Depends, HTTPException, WebSocketException
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pydantic import BaseModel

from business.entity.user.user_entity import UserEntity, UserRole
from main.dependency_container import DepContainer


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
SECRET_KEY = None


def setup_auth():
    global SECRET_KEY
    SECRET_KEY = os.environ.get("AUTH_SECRET_KEY")


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserEntity:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = inject.instance(DepContainer).user_repo.get(user_email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[UserEntity, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_user_from_websocket(
        token: str
):
    try:
        return await get_current_active_user(await get_current_user(token))
    except HTTPException as e:
        raise WebSocketException(code=1008, reason=e.detail)


async def get_current_admin_user(
        current_user: Annotated[UserEntity, Depends(get_current_active_user)],
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=401, detail="User is not an admin")
    return current_user


def get_password_hash(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=480)  # 8 hours
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def send_verification_code(email):
    verification = inject.instance(DepContainer).twilio_client.verify.v2.services(
        os.environ.get("TWILIO_VERIFY_SERVICE_SID")
    ).verifications.create(to=email, channel="email")
    assert verification.status == 'pending'


def check_verification_code(email, code):
    verification = inject.instance(DepContainer).twilio_client.verify.v2.services(
        os.environ.get("TWILIO_VERIFY_SERVICE_SID")).verification_checks.create(
        to=email, code=code)
    return verification.status == 'approved'
