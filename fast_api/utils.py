# Installed packages
from jose import JWTError, jwt
import time
import logging

# Local packages
from .user.config import SECRET_KEY, ALGORITHM
from .user.constants import Token


def decode_access_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded_token.get("expires", 0) >= time.time():
            # Токен действителен
            return decoded_token
        else:
            return None
    except JWTError:
        logging.error("auth jwt error")
        return None
