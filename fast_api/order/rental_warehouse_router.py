# Import necessary libraries and modules
from fastapi import APIRouter, Query, File, Depends, UploadFile
from fastapi.params import Path
from typing import Union, Optional, List
from fastapi_pagination import Page, paginate, add_pagination
from bson import ObjectId
from datetime import datetime, timedelta
from ..order import service
import json

### Local packages
from ..user.models import DBUser
from ..user.constants import Roles
from ..dependencies import get_current_user, check_role_access
from .models import RentalData,RentCellByClient

# Create a router to handle requests related to rentals
rental_router = APIRouter(prefix="/rental", tags=["rental"])

@rental_router.post("/cell/",response_model=dict)
async def rent_cell_by_client(data:RentCellByClient,current_user:DBUser=Depends(get_current_user)):
    check_role_access(current_user.role,[Roles.admin,Roles.manager,Roles.client])
    await service.register_order(order=data.dict())
    return {"success":f"successfully created order by {current_user.role}"}

# Handler for POST requests to create a rental order
@rental_router.post("/", response_model=dict)
async def create_rental_order(rent_data: RentalData, current_user: DBUser = Depends(get_current_user)):
    # Check the access for the current user based on their role
    check_role_access(current_user.role, [Roles.admin, Roles.manager, Roles.salesman])
    # Convert rental data to a dictionary
    rent_data = rent_data.dict()
    rent_data["status"] = "rental_order"
    # Register a rental order and get its identifier
    order_id = await service.register_order(order=rent_data)
    return {"success": f"Successfully created an order with the ID {order_id}"}

# Handler for GET requests to retrieve a rental order by its ID
@rental_router.get("/{order_id}", response_model=dict)
async def get_rental_order_by_id(order_id: str, current_user: DBUser = Depends(get_current_user)):
    # Check the access for the current user based on their role
    check_role_access(current_user.role, [Roles.admin, Roles.manager, Roles.client])
    # Get rental order data by its ID
    order_data = await service.get_order_by_id(order_id=order_id)
    return order_data

# Handler for GET requests to retrieve all rental orders
@rental_router.get("/", response_model=list)
async def get_all_rental_orders(current_user: DBUser = Depends(get_current_user)):
    # Check the access for the current user based on their role
    check_role_access(current_user.role, [Roles.manager, Roles.admin, Roles.director, Roles.client])
    # Retrieve all rental orders associated with the current user
    orders = await service.return_all_orders(user_id=current_user.id, role=current_user.role, company=current_user.company, warehouse=current_user.warehouse)
    return orders
