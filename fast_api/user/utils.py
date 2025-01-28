# Installed packages
from passlib.context import CryptContext
from jose import jwt
import time

# Local packages
from ..exceptions import InvalidCredentialsException
from .config import ACCESS_TOKEN_EXPIRE_SECONDS, SECRET_KEY, ALGORITHM,REFRESH_TOKEN_EXPIRE_DAY
from .constants import Users, Token
from ..database import temporary_tokens_collection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_access_token(user_id: str):
    expire = time.time() + ACCESS_TOKEN_EXPIRE_SECONDS
    payload = {"sub": user_id, Token.expires: expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

async def create_refresh_token(user_email:str):
    expire = time.time() + REFRESH_TOKEN_EXPIRE_DAY
    payload = {"sub": user_email, Token.expires: expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    # refresh ={"refresh_token":token}
    # await temporary_tokens_collection.insert_one(refresh)
    return token

def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


async def verify_password_exception(plain_password: str, hashed_password: str):
    if not verify_password(plain_password, hashed_password):
        raise InvalidCredentialsException


def password_validation(passwd) -> str | None:
    special_symbols = ("$", "@", "#", "%","*","/","-",",", "." , "+","^", "&", "?", "(",")","=","_","!","~")
    if len(passwd) < 6:
        raise ValueError("length should be at least 6")
    if len(passwd) > 20:
        raise ValueError("length should be not be greater than 20")
    if not any(char.isdigit() for char in passwd):
        raise ValueError("Password should have at least one numeral")
    if not any(char.isupper() for char in passwd):
        raise ValueError("Password should have at least one uppercase letter")
    if not any(char.islower() for char in passwd):
        raise ValueError("Password should have at least one lowercase letter")
    if not any(char in special_symbols for char in passwd):
        raise ValueError("Password should have at least one of the symbols $@#")
    return passwd
