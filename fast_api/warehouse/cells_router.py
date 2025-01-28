from fastapi import APIRouter, Depends
from bson.objectid import ObjectId
from fastapi_pagination import Page, paginate, add_pagination
from ..dependencies import (
    check_role_access,
    get_exception_responses,
    get_current_user,
    user_has_permission
)
from .exceptions import CellLengthNotCorrect,CellWidthNotCorrect
from ..user.models import DBUser
from ..user.constants import Roles
from .models import Cells, CellUpdate
from .service import (get_cell_by_id, create_cell, 
                      get_all_cells, update_cells,get_floor_by_id,
                      delete_cell_by_id)

# Create an APIRouter instance for warehouse-related operations.
cell_router = APIRouter(
    prefix="/cell", tags=["cell"]
)

# Endpoint to create a new cell.
@cell_router.post("/", response_model=dict)
async def create_cell_data(data: Cells, current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"create_cell")
    # check_role_access(current_user.role, [Roles.manager, Roles.director, Roles.admin])
    # Check if the specified floor (by ID) exists.
    floor_data =await get_floor_by_id(data.floor_id)
    if  data.cell_length != 0 and data.cell_height >floor_data["floor_length"]:
        raise CellLengthNotCorrect
    if data.cell_width != 0 and data.cell_width > floor_data["floor_width"]:
        raise CellWidthNotCorrect
    if data.cell_length ==0:
        data.cell_length =floor_data["floor_length"]
    if data.cell_width ==0:
        data.cell_width = floor_data["floor_width"]
    data.cell_price +=floor_data["floor_max_price"]
    cell_volume = data.cell_height*data.cell_length*data.cell_width
    # Create a new cell based on the provided data.
    data = data.dict()
    data["products"]=[]
    data["cell_volume"]=cell_volume
    await create_cell(data=data)
    # Return a success message.
    return {"success": "Successfully created cell data"}

# Endpoint to get cell data by its ID.
@cell_router.get("/{cell_id}", response_model=dict)
async def get_data_by_cell_data(cell_id: str, current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_cell")
    # Get cell data by its ID.
    res = await get_cell_by_id(id=cell_id)
    # Return the retrieved cell data.
    return res

# Endpoint to get all cell data.
@cell_router.get("/", response_model=Page[dict])
async def get_all_cell_data(current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_all_cell")
    # Retrieve all cell data.
    res = await get_all_cells({})
    # Return a list of all cell data.
    return paginate(res)

# Endpoint to update cell data by ID.
@cell_router.put("/{cell_id}", response_model=dict)
async def update_data_in_cell(cell_id: str, data: CellUpdate, current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"update_cell")
    query =None
    # Define the query to identify the cell by its ID.
    query = {"_id": ObjectId(cell_id)}
    data = data.dict()
    cell_d ={}
    for key,val in data.items():
        if val !=None and val !="string" and val !=0:
            cell_d[key]=val
    # Update the cell data with the provided values from CellUpdate.
    await update_cells(query=query, data=cell_d)
    # Return a success message.
    return {"success": "Successfully updated cell data"}


@cell_router.delete("/{cell_id}",response_model=dict)
async def delete_cell(cell_id:str,current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"delete_cell")
    await delete_cell_by_id(id=cell_id)
    return {"success":f"successfully deleted cell by {cell_id}"}

@cell_router.get("/floor/{floor_id}",response_model=Page[dict])
async def get_cells_by_floorid(floor_id:str,current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_all_cell")
    cells = await get_all_cells(query={"floor_id":floor_id})
    return paginate(cells)

add_pagination(cell_router)