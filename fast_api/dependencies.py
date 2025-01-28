# Installed packages
from fastapi import UploadFile,Cookie
from typing import Type, List
import uuid
import magic
import string
import random
import os
import shutil
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from bson.objectid import ObjectId

# Local packages
from .user.service import get_user_by,get_all_roles_in_company
from .user.constants import Users, Roles
from .user import utils as user_utils
from . import utils
from .exceptions import (
    PermissionException,
    BaseAPIException,
    InvalidCredentialsException,
    NotFoundException,
    ConflictException,
    AlreadyCheckedException,
    QualityCheckFailed,
    RequestEntityTooLargeException,
    EmptyFileUploadException,
    UnsupportedMediaTypeException,
    TokenInvalidException,
)
from .product.constants import Products
from .config import ALLOWED_MEDIA_TYPES, IMAGE_DIRECTORY
from .constants import Errors
from .database import users_collection

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        if token is None:
            raise HTTPException(status_code=403, detail=Errors.invalid_token)
        payload = utils.decode_access_token(token)
        if not payload:
            raise HTTPException(status_code=403, detail=Errors.invalid_token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail=Errors.cntv_credentials)
    except JWTError:
        raise HTTPException(status_code=401, detail=Errors.cntv_credentials)
    user = await get_user_by(Users.email, username)
    return user


def get_exception_responses(*args: Type[BaseAPIException]) -> dict:
    """Given BaseAPIException classes, return a dict of responses used on FastAPI endpoint definition, with the format:
    {statuscode: schema, statuscode: schema, ...}"""
    responses = dict()
    for cls in args:
        responses.update(cls.response_model())
    return responses


def check_role_access(user_role: str, roles: list):
    if user_role not in roles:
        raise PermissionException

async def user_has_permission(query:dict, required_permission: str):
    roles = await get_all_roles_in_company(query=query)
    if len(roles)==0:
        raise HTTPException(status_code=403,detail="in company not found this role")
    role = roles[0]
    # role = await get_role_by_id(id=role_id)
    # Получение списка разрешений из объекта роли
    permissions = [perm["permission_name"] for perm in role["permissions"]]
    if required_permission not in permissions:
        raise PermissionException




def check_admin_n_manager_access_without_exc(role):
    return role != Roles.admin and role != Roles.manager and role != Roles.director


async def check_access_n_credentials(
    username, current_username, password, hashed_password, user_role
):
    if username != current_username or not user_utils.verify_password(
        password, hashed_password
    ):
        if user_role == Roles.admin or user_role == Roles.manager:
            pass
        elif (
            user_role != Roles.admin
            and user_role != Roles.manager
            and username != current_username
        ):
            raise PermissionException
        else:
            raise InvalidCredentialsException


def check_admin_n_user_access(user_role, username, current_username):
    if user_role != Roles.admin and username != current_username:
        raise PermissionException


async def check_manager_permission(role: str, user_id: str):
    user = await users_collection.find_one({Users.id_: ObjectId(user_id)})
    if (
        user
        and user[Users.role]
        in [Roles.manager, Roles.admin, Roles.director, Roles.salesman]
        and role not in [Roles.director, Roles.admin]
    ):
        raise PermissionException


def check_data(product):
    if not product:
        raise NotFoundException
    elif not product.get("date_of_arrival"):
        raise ConflictException
    elif product.get("quality_check_passed") is not None:
        raise AlreadyCheckedException


def is_quality_checked(product):
    if "quality_check_passed" not in product or not product["quality_check_passed"]:
        raise QualityCheckFailed


def validate_file_size(file: UploadFile, max_size):
    if file.size > max_size:
        raise RequestEntityTooLargeException


def validate_emptiness(files: list[UploadFile]):
    if not len(files):
        raise EmptyFileUploadException


def validate_file_format(file: UploadFile):
    file_type = magic.from_buffer(file.file.read(2048), mime=True)
    print(file_type)
    if file_type not in ALLOWED_MEDIA_TYPES:
        raise UnsupportedMediaTypeException


# def encode_files(files: list[UploadFile]) -> list[str]:
#     validate_emptiness(files)

#     for file in files:
#         validate_file_size(file)
#         validate_file_format(file)

#     encoded_files = []
#     for file in files:
#         file_data = file.file.read()
#         file_data_base64 = base64.b64encode(file_data).decode('utf-8')
#         encoded_files.append(file_data_base64)
#     return encoded_files


def upload_files(
    files: list[UploadFile], id: str, max_size: int, directory: str
) -> List[str]:
    validate_emptiness(files)

    file_paths = []
    files_dir = os.path.join("data", directory)
    os.makedirs(files_dir, exist_ok=True)
    # Perform file upload limit check
    for file in files:
        validate_file_size(file, max_size)
        #             validate_media_type(file.filename)
        validate_file_format(file)
    file_sub_dir = os.path.join(files_dir, id)
    os.makedirs(file_sub_dir, exist_ok=True)

    # Process file uploads
    for file in files:
        file_path = os.path.join(file_sub_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_paths.append(file_path)
    return file_paths


def generate_sku(product):
    unique_id = str(uuid.uuid4()).replace("-", "")

    sku = (
        f"{product[Products.product_name][:3]}-{product[Products.packing_type][:3]}-"
        f"{unique_id[:4]}-{product[Products.weight]}"
    )

    sku = sku[:20]

    return sku


async def generate_qr_code(count: int) -> list:
    res = []
    for _ in range(count):
        res.append({"qr_code": str(ObjectId())})
    return res


async def generate_unique_url():
    return str(uuid.uuid4())


async def check_order_creation_token(token: str):
    if not token:
        raise TokenInvalidException


async def check_access_by_product_instance(warehouse_team: dict, worker_id: str):
    worker_ids = [worker[Users.id] for worker in warehouse_team]
    if worker_id not in worker_ids:
        raise PermissionException


def upload_files_for_place(
    files: List[UploadFile], current_place: str, max_size
) -> List[str]:
    validate_emptiness(files)
    file_paths = []
    image_dir = os.path.join("data", IMAGE_DIRECTORY)
    os.makedirs(image_dir, exist_ok=True)
    # Perform file upload limit check
    for file in files:
        validate_file_size(file, max_size)
        #            validate_media_type(file.filename)
        validate_file_format(file)
    unsuitable_place_dir = os.path.join(image_dir, current_place)
    os.makedirs(unsuitable_place_dir, exist_ok=True)
    for file in files:
        file_path = os.path.join(unsuitable_place_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_paths.append(file_path)
    return file_paths

async def generate_random_password()->str:
    length =10
    # Define the character set for the password
    characters = string.ascii_letters + string.digits + string.punctuation
    # Generate a random password by selecting characters from the set
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


###Generate_random_code for verification code
async def generate_random_code() -> int:
    return random.randint(100000, 999999)
