# Installed packages
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate, add_pagination
import logging

# Local packages
from ..order.email_sender import send_email_to_client
from .models import (
    Company,
    ReturnCompany,
    UpdateCompany,
    CompanyWithStatus,
    DeleteWarehouse,
)
from . import service
from . import constants
from ..dependencies import (
    check_role_access,
    get_exception_responses,
    get_current_user,
    generate_random_code,
    user_has_permission
)
from ..exceptions import (
    UnauthorizedException,
    PermissionException,
    DuplicateKeyException,
)
from ..responses import Success
# from ..database import db
from ..user.constants import Users, Roles
from ..user.models import DBUser, WebFounder, UserWithID, DBUserWithoutId
from ..user.service import (
    register_founder,
    check_founder_exists,
    remove_all_user_in_company,
    # remove_all_users_in_warehouse,
    # get_all_users_by_warehouse,
    remove_user
)
from ..user.utils import hash_password
from ..order.service import remove_all_orders_in_company
from ..product.service import remove_all_products_in_company
# from ..database import client
# Create an APIRouter instance with a specified prefix and tags.
company_router = APIRouter(
    prefix=constants.Company.prefix, tags=[constants.Company.company]
)

# Define a GET endpoint to retrieve the current user's company.
@company_router.get(
    "/",
    response_model=ReturnCompany,
    responses=get_exception_responses(UnauthorizedException, PermissionException),
)
async def get_currents_company(current_user: DBUser = Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query=query,required_permission="view_own_company")
    # Call the service.get_company() function to fetch the user's company data and return it.
    return await service.get_company(current_user.company)


@company_router.post(
    "/",
    response_model=Success,
    responses=get_exception_responses(DuplicateKeyException),
)
async def create_company(
    founder: WebFounder,
    company: Company,
    # files: Annotated[Optional[List[UploadFile]], File()] = None,
):
    company_id =None
    inserted_id = None
    try:
        await check_founder_exists(founder.email)
        await service.check_company_exists(company.company_name)
        # Generate a random verification code
        user=founder.dict()
        verification_code = await generate_random_code()
        user["verification_code"]=verification_code
        inserted_id = await register_founder(
            DBUserWithoutId(
                **{
                    **user,
                    Users.hashed_password: hash_password(founder.password),
                    Users.role: Roles.director,
                    Users.company: company.company_name,
                }
            )
        )
        # company["logo"]=file_paths
        company_id = await service.create_company_(
            CompanyWithStatus(
                **{
                    **company.dict(),
                    constants.Company.status: constants.Messages.active,
                }
            )
        )
        if company_id is None:
            await remove_user(inserted_id)
        # Define an HTML email template with the verification code
        html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
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
            "office_email": company.office_email,
            "recipient_email": user["email"],
            "description": str(html_content),
            "subject": "Verification Code",
        }
        #Send the email to the client
        await send_email_to_client(email_data=email_data)
    except Exception as e:
        if company_id is not None and inserted_id is not None:
            await remove_user(inserted_id)
            await service.delete_company_with_id(company_id)
        logging.error("create_company_and_founder err: %s",e)
        raise e
    return {constants.Messages.message: constants.Messages.cmpn_crtd_scs}

# Define a PUT endpoint to update company data.
@company_router.put(
    "/",
    response_model=Success,
    responses=get_exception_responses(UnauthorizedException, PermissionException),
)
async def update_company_data(
    data: UpdateCompany, current_user: DBUser = Depends(get_current_user)
):
    # Check if the current user has the necessary role to update company data.\
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query=query,required_permission="update_company_data")
    # check_role_access(current_user.role, [Roles.director, Roles.admin])
    # Create a dictionary to store updated data, excluding empty or null values.
    update_data = data.dict()
    update_dataa = {}
    for key, value in update_data.items():
        if value is not None and value != "" and value != "string" and value != 0:
            update_dataa[key] = value
    # Call the service function to update company data with the filtered values.
    await service.update_data(current_user.company, update_dataa)
    # Return a success message after successfully updating the company data.
    return {constants.Messages.message: constants.Messages.cmpn_data_chngd_scs}


# Define a DELETE endpoint to delete a company.
@company_router.delete("/")
async def delete_company(current_user: DBUser = Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    # Check if the current user has the necessary role to delete the company.
    await user_has_permission(query=query,required_permission="delete_company")
    # check_role_access(current_user.role, [Roles.director])
    # Call service functions to delete the company and associated data.
    await service.delete_company(current_user.company)
    await remove_all_user_in_company(current_user.company)
    await remove_all_orders_in_company(current_user.company)
    await remove_all_products_in_company(current_user.company)
    # Return a success message after successfully deleting the company.
    return {"message": "Company was successfully deleted"}


add_pagination(company_router)
