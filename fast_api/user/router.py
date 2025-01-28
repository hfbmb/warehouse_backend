# Import necessary packages and modules
from fastapi import Depends, APIRouter, Cookie,HTTPException
from fastapi.responses import JSONResponse
from pydantic import Json
from typing import Annotated, Optional
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import Page, paginate, add_pagination

# Local packages and custom exceptions
from ..order.email_sender import send_email_to_client
from ..utils import decode_access_token
from ..redis import redis_set, redis_get
from ..config import MAX_IMAGE_UPLOAD_SIZE
from ..company.service import warehouse_exists,get_company
from ..dependencies import (
    get_exception_responses,
    get_current_user,
    check_role_access,
    check_access_n_credentials,
    check_manager_permission,
    generate_random_code,
    user_has_permission
    # upload_files_for_place,
)
from ..exceptions import (
    UnauthorizedException,
    PermissionException,
    NotFoundException,
    AlreadyExistsException,
    InvalidCredentialsException,
    DoesNotExist,
)
from ..responses import Success
from .models import (
    UserWithID,
    DBUser,
    WebUser,
    UserOut,
    UserChangePassword,
    UserUpdate,
    ImageCreate,
    ForgotPassword
)
from . import service
from . import utils
from . import constants

# Create an API router for user-related endpoints
router = APIRouter(prefix="/users", tags=["users"])

# Endpoint to get a paginated list of all users
# Пример использования user_has_permission вместо check_role_access:
@router.get(
    "/",
    response_model=Page[UserWithID],
    responses=get_exception_responses(UnauthorizedException, PermissionException),
)
async def get_all_users(user: DBUser = Depends(get_current_user)):
    # Предположим, что у вас есть разрешение "view_all_users" для просмотра всех пользователей.
    query={
        "role_name":user.role,
        "company_name":user.company
    }
    await user_has_permission(query, "view_all_users")
    return paginate(await service.get_all_users_by_company(user.company))

# Endpoint to get a user by their ID
@router.get(
    "/{user_id}",
    response_model=dict,
    responses=get_exception_responses(UnauthorizedException, PermissionException),
)
async def get_user_by_id(
    user_id: str, current_user: DBUser = Depends(get_current_user)
):
    query={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query=query,required_permission="view_user_by_id")
    # roles = [constants.Roles.director, constants.Roles.admin, constants.Roles.manager]
    # check_role_access(current_user.role, roles)
    user = await service.get_user_by(constants.Users.id_, user_id)
    return user.dict()

# Endpoint to get the current user's information
@router.get(
    "/user/info",
    response_model=dict,
    responses=get_exception_responses(UnauthorizedException, PermissionException),
)
async def get_user(user: DBUser = Depends(get_current_user)):
    return user.dict()

# Endpoint to register a new user
@router.post(
    "/",
    responses=get_exception_responses(
        UnauthorizedException,
        AlreadyExistsException,
        PermissionException,
        NotFoundException,
    ),
)
async def register_user(
    request: WebUser,  # Receive user registration data from the request
    current_user: DBUser = Depends(get_current_user),  # Get the current user making the request
):
    # Check if the current user has the required role to create a new user
    query={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query=query,required_permission="register_user")
    roles = await service.get_all_roles_in_company({"role_name":request.role,"company_name":current_user.company})
    if len(roles)==0:
        raise HTTPException(status_code=400,detail="this role not found in company")
    # check_role_access(
    #     current_user.role,
    #     [constants.Roles.director, constants.Roles.admin, constants.Roles.manager],
    # )
    # Hash the user's password for security
    hashed_password = utils.hash_password(request.password)
    # Create a dictionary representing the user document
    user = request.dict()
    # Add the hashed password to the user document
    user[constants.Users.hashed_password] = hashed_password
    # Set the company field based on the current user's company
    user[constants.Users.company] = current_user.company
    # Remove the plaintext password from the user data
    user.pop(constants.Users.password)
    # Retrieve company data for the user's company
    company_data = await get_company(name=user["company"])
    # If the user's role is "salesman" and the specified warehouse doesn't exist, remove the warehouse field
    if user[constants.Users.role] == constants.Roles.salesman and not await warehouse_exists(
        current_user.company, request.warehouse
    ):
        user.pop(constants.Users.warehouse)
    # Generate a random verification code
    verification_code = await generate_random_code()
    user["verification_code"]=verification_code
    user["is_confirmed"]=False
    # Define an HTML email template with the verification code
    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Verification Code</title>
        </head>
        <body>
            <p>Dear Client,</p>
            <p>Your verification code is: <strong>{verification_code}</strong></p>
            <p>Please use this code to complete your registration.</p>
            <a href="https://warehouse-main.vercel.app/auth/verification">Use this link</a> 
        </body>
        </html>
    """
    # Prepare email data for sending the verification code to the client
    email_data = {
        "office_email": company_data["office_email"],
        "recipient_email": user["email"],
        "description": str(html_content),
        "subject": "Verification Code",
    }
    # Insert the user document into MongoDB
    await service.register_user_(user)
    # Send the email to the client
    await send_email_to_client(email_data=email_data)
    # Return a success message
    return {"message": "User registered successfully"}

@router.put("/{verification_code}",response_model=dict)
async def confirm_code(verification_code:str,email:str):
    query ={"email":email,
            "verification_code":int(verification_code)}
    user = await service.custom_get_user_info_get(query=query)
    if user:
        # user["is_confirmed"]=True
        await service.update_user(user_id=user["id"],data={"is_confirmed":True})
        return {"success":"email successfully verified"}
    else:
        raise HTTPException(400,detail="email or verification code is not correct")

# Endpoint for user login
@router.post(
    "/login",
    responses=get_exception_responses(InvalidCredentialsException),
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Get username and password from request body
    username = form_data.username
    password = form_data.password

    # Retrieve user document from MongoDB
    user = await service.get_user_by(constants.Users.email, username)
    if user.is_confirmed ==False:
        raise HTTPException(403,detail="you don't have confirmed verification code")
    # Check if user exists and password is correct
    await utils.verify_password_exception(password, user.hashed_password)
    # Return access token and refresh token
    access_token = await utils.create_access_token(username)
    refresh_token = await utils.create_refresh_token(username)
    # response = JSONResponse(content={"access_token": access_token, "refresh_token": refresh_token})
    # response.set_cookie(key="token", value=access_token)
    # await redis_set(username,{"refresh_token":refresh_token})

    return {"access_token":access_token}

# Endpoint for user logout
@router.post("/logout")
async def logout(response: JSONResponse, access_token: str = Cookie(None)):
    # Remove the access_token cookie to log the user out
    response.delete_cookie(key="access_token")
    # Return a message indicating successful logout
    return {"message": "Logged out successfully"}

# Endpoint to refresh the access token using a refresh token
@router.post("/take/access_token/{refresh_token}", response_model=dict)
async def refresh_access_token(
    refresh_token: str):
    # refresh_token =await redis_get(current_user.email)
    # # access_token =str
    # if refresh_token:
    #     access_token = await utils.create_access_token(current_user.email)
    #     response = JSONResponse(content={"access_token": access_token, "refresh_token": refresh_token})
    #     response.set_cookie(key="access_token", value=access_token)
    tokens =await service.refresh_new_access_token(refresh_token)
    return  tokens
    #     return response
    # else:
    #     raise InvalidCredentialsException()
# create start with an order


# Endpoint to delete a user by their ID
@router.delete(
    "/{user_id}",
    response_model=Success,
    responses=get_exception_responses(
        UnauthorizedException, DoesNotExist, PermissionException
    ),
)
async def delete_user(user_id: str, user: DBUser = Depends(get_current_user)):
    # Check user's permission and role
    query={
        "role_name":user.role,
        "company_name":user.company
    }
    await user_has_permission(query=query,required_permission="delete_user")
    # check_role_access(
    #     user.role,
    #     [constants.Roles.director, constants.Roles.admin, constants.Roles.manager],
    # )
    await check_manager_permission(
        user.role, user_id
    )  # Manager cannot delete another manager
    # Delete the user by their ID
    await service.remove_user(user_id)
    return {
        constants.Messages.message: constants.Messages.deleted,
        constants.Users.id: user_id,
    }

# Endpoint to change a user's password
@router.post(
    "/password/change",
    response_model=Success,
    responses=get_exception_responses(
        UnauthorizedException, PermissionException, InvalidCredentialsException
    ),
)
async def change_password(
    user: UserChangePassword, current_user: DBUser = Depends(get_current_user)
):
    # Check access and credentials before changing the password
    await check_access_n_credentials(
        user.email,
        current_user.email,
        user.old_password,
        current_user.hashed_password,
        current_user.role,
    )
    # Hash the new password and update it
    hashed_password = utils.hash_password(user.new_password)
    await service.change_password_(user.email, hashed_password)
    return {
        constants.Messages.message: constants.Messages.pswrd_chngd,
        constants.Users.new_pswrd: user.new_password,
    }

# Placeholder for password recovery functionality
@router.put("/password/forgot",response_model =dict)
async def forgot_password(email:str):
    user =await service.custom_get_user_info_get({"email":email})
    # Define an HTML email template with the verification code
    
    company_data = await get_company(name=user["company"])
    verification_code = await generate_random_code()
    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Verification Code</title>
        </head>
        <body>
            <p>Dear Client,</p>
            <p>Your verification code is: <strong>{verification_code}</strong></p>
            <p>Please use this code to complete your registration.</p>
        </body>
        </html>
    """
    # Prepare email data for sending the verification code to the client
    email_data = {
        "office_email": company_data,
        "recipient_email": user["email"],
        "description": str(html_content),
        "subject": "Verification Code",
    }
    # user.pop("hashed_password")
    # user["is_confirmed"]=False
    await service.update_user(user_id=user["id"],data={"verification_code":verification_code})
    await send_email_to_client(email_data=email_data)
    return {"success":"we send verification code to email"}

@router.put("/verification/code",response_model=dict)
async def change_password_with_verification_code(verf_data:ForgotPassword):
    query ={"email":verf_data.email,
            "verification_code":int(verf_data.verification_code)}
    user = await service.custom_get_user_info_get(query=query)
    hashed_password = utils.hash_password(verf_data.new_password)
    user["is_confirmed"]=True
    user["hashed_password"]= hashed_password
    await service.update_user(user_id=user["id"],data=user)
    return {"success":"successfully updated user data"}
        

# Endpoint to update a user's data by their ID
@router.put("/{user_id}")
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: DBUser = Depends(get_current_user),
):
    # Check user's role and access before updating the user's data
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query=query,required_permission="update_user_data")
    # check_role_access(
    #     current_user.role,
    #     [constants.Roles.director, constants.Roles.admin, constants.Roles.manager],
    # )
    # Update the user's data with the provided information
    await service.update_user(user_id, user_data.dict())
    return {"success": "User was successfully updated"}

# Add pagination to the router
add_pagination(router)
