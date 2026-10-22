import asyncio
import datetime
import logging
from typing import Annotated

import inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr, BaseModel, Field
from sendgrid import Email, To, Content, Mail

from business.entity.user.user_entity import UserEntity, UserRole
from interface.auth.auth import verify_password, create_access_token, Token, get_password_hash, \
    send_verification_code, check_verification_code, get_current_admin_user
from main.dependency_container import DepContainer

router = APIRouter(prefix="/auth", tags=["auth"])
DEFAULT_CREDITS = 20
logger = logging.getLogger("hekades")
INCORRECT_CREDENTIALS = "Incorrect username or password"


class RegisterUserModel(BaseModel):
    email: EmailStr = Field(..., title="The email of the user")
    title: str = Field(..., min_length=1, title="The title of the user")
    full_name: str = Field(..., min_length=1, title="The full name of the user")
    plain_password: str = Field(..., min_length=1, title="The plain password of the user")
    dob: datetime.datetime = Field(..., title="The date of birth of the user")
    country: str = Field(..., title="The country of the user")
    city: str = Field(..., title="The city of the user")
    institution: str = Field(..., min_length=1, title="The institution of the user")
    department: str = Field(..., min_length=1, title="The department of the user")
    cell_phone: str = Field(..., min_length=1, title="The cell phone of the user")
    address: str = Field(..., title="The address of the user")
    occupation: str = Field(..., title="The occupation of the user")
    branch: str = Field(..., title="The branch of the user")
    ssn: str = Field(..., title="The social security number of the user")


@router.post("/login")  # Don't change the path, used in oauth2 scheme setup too
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Username is email.
    https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/#get-the-username-and-password
    """

    user = inject.instance(DepContainer).user_repo.get(user_email=form_data.username)
    if user is None:
        raise HTTPException(status_code=400, detail=INCORRECT_CREDENTIALS)

    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is not verified")

    hashed_password = inject.instance(DepContainer).user_repo.get_user_password(user_email=form_data.username)
    if not verify_password(form_data.password, hashed_password):
        raise HTTPException(status_code=400, detail=INCORRECT_CREDENTIALS)
    access_token = create_access_token(
        data={"sub": user.email}
    )

    return Token(access_token=access_token, token_type="bearer")


@router.post("/register")
async def register(model: RegisterUserModel):
    try:
        inject.instance(DepContainer).user_repo.add(
            user=UserEntity(
                full_name=model.full_name,
                email=model.email,
                credits=DEFAULT_CREDITS,
                created_at=datetime.datetime.now(),
                is_active=False,
                profile_picture=None,
                role=UserRole.USER,
                dob=model.dob,
                country=model.country,
                city=model.city,
                institution=model.institution,
                department=model.department,
                cell_phone=model.cell_phone,
                address=model.address,
                occupation=model.occupation,
                branch=model.branch,
                ssn=model.ssn,
                title=model.title
            ),
            hashed_password=get_password_hash(model.plain_password),
        )
        await asyncio.to_thread(send_verification_code, model.email)
    except ValueError:
        raise HTTPException(status_code=400, detail="User already exists")


@router.get("/verify_email")
async def verify(code: str, email: str):
    try:
        verified = await asyncio.to_thread(check_verification_code, email, code)
    except Exception as e:
        logger.error("Error verifying user", exc_info=e)
        raise HTTPException(status_code=400, detail="Incorrect verification code")
    if not verified:
        raise HTTPException(status_code=400, detail="Incorrect verification code")
    send_user_to_boss(email)


class AcceptModel(BaseModel):
    email: str


@router.post("/accept_user")
def accept_user(model: AcceptModel, user: UserEntity = Depends(get_current_admin_user)):
    inject.instance(DepContainer).user_repo.set_user_active(model.email)


def send_user_to_boss(email: str):
    user = inject.instance(DepContainer).user_repo.get(user_email=email)

    from_email = Email("noreply@hekades.com")  # Change to your verified sender
    to_email = To("nbuyuktuna@hekades.com")  # Change to your recipient
    subject = "Yeni kullancı kaydı!"
    content = Content("text/plain", f"""
        Yeni bir kullanıcı kaydı yapıldı.
        Kullanıcı adı: {user.full_name}
        Email: {user.email}
        Ünvan: {user.title}
        Doğum tarihi: {user.dob}
        Ülke: {user.country}
        Şehir: {user.city}
        Kurum: {user.institution}
        Departman: {user.department}
        Cep telefonu: {user.cell_phone}
        Adres: {user.address}
        Meslek: {user.occupation}
        Branş: {user.branch}
        Şube: {user.branch}
        TC Kimlik No: {user.ssn}
        
    
    """)
    mail = Mail(from_email, to_email, subject, content)
    mail_json = mail.get()

    # Send an HTTP POST request to /mail/send
    response = inject.instance(DepContainer).sendgrid_client.client.mail.send.post(request_body=mail_json)
    logger.info(f"Email sent to boss for new user {email}: {response.status_code}")
