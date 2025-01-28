from fastapi import APIRouter, Depends
from bson.objectid import ObjectId
from fastapi_pagination import Page, paginate, add_pagination
from ..dependencies import (
    check_role_access,
    get_exception_responses,
    get_current_user,
    user_has_permission
)
from ..user.models import DBUser
from ..user.constants import Roles
from .models import Category, CategoryUpdate
from .service import (check_warehouse_data_by_id,
                      create_category,
                      get_category_by_id,
                      get_all_categories,delete_category_by_id,
                      current_user_warehouse,
                      update_category)

# Create an APIRouter instance for warehouse-related operations.
category_router = APIRouter(
    prefix="/category", tags=["category"]
)

# Endpoint to create a new category.
@category_router.post("/", response_model=dict)
async def create_category_api(cat_data: Category, current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"create_category")
    # Convert category data to a dictionary and extract warehouse_id.
    cat_data = cat_data.dict()
    warehouse_id = cat_data["warehouse_id"]
    # Check if the specified warehouse (by ID) exists.
    await check_warehouse_data_by_id(id=warehouse_id)
    # Create a new category based on the provided data.
    await create_category(cat_data)

    # Return a success message.
    return {"success": "Successfully created category"}

# Endpoint to get category data by its ID.
@category_router.get("/{category_id}", response_model=dict)
async def get_category_data_warehouse(category_id: str, current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_category")
    # Get category data by its ID.
    result = await get_category_by_id(category_id)
    # Return the retrieved category data.
    return result

# Endpoint to get all category data within the user's warehouse.
@category_router.get('/', response_model=Page[dict])
async def get_all_category_data(current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_all_category")
    query =None
    # Get the user's warehouse data based on their company and warehouse names.
    warehouse_data = await current_user_warehouse({"company_name": current_user.company,
                                                   "warehouse_name": current_user.warehouse})
    # Define the query to filter categories by warehouse_id.
    query = {"warehouse_id": warehouse_data["id"]}
    # Retrieve all category data based on the warehouse query.
    result = await get_all_categories(query=query)
    # Return a list of all category data within the user's warehouse.
    return paginate(result)

# Endpoint to update category data by ID.
@category_router.put("/{category_id}", response_model=dict)
async def update_category_data(category_id: str, data: CategoryUpdate, current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"update_category")
    query=None
    # Convert CategoryUpdate data to a dictionary.
    data = data.dict()
    cat_d ={}
    for key,val in data.items():
        if val !=None and val !="string" and val !=0:
            cat_d[key]=val
    # Define the query to identify the category by its ID.
    query = {"_id": ObjectId(category_id)}
    # Update the category data with the provided values from CategoryUpdate.
    await update_category(query=query, data=cat_d)
    # Return a success message.
    return {"success": "Successfully updated category data"}

@category_router.delete("/{category_id}",response_model=dict)
async def delete_category(category_id:str,current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"delete_category")
    await delete_category_by_id(id=category_id)
    return {"success":f"successfully deleted category by {category_id}"}


add_pagination(category_router)