# Import necessary FastAPI modules and dependencies
from fastapi import APIRouter, Depends,HTTPException
from bson.objectid import ObjectId
from datetime import datetime,timedelta
from fastapi_pagination import Page, paginate, add_pagination

# Import data models, constants, and service functions from your project's modules
from ..websocket.router import manager
from ..order.email_sender import send_email_to_client,scheduler,IntervalTrigger
from .shpmemt_model import ShipmentOrder, Update_Shipment_order,ShipmentOrderWithID
from .shipment_constants import Shipment
from .shipment_service import (
    create_shipment,
    get_all_orders,
    get_shipment_order_by_id,
    delete_shipment_order_by_id,
    update_shipment_order_by_id,
)
from ..user.models import DBUser
from ..user.constants import Roles
from ..user.service import update_user_order_status
from ..dependencies import get_current_user, check_role_access
from ..responses import Success
from ..company.service import check_order_company_and_or_warehouse,get_company

# Create an APIRouter instance with a prefix and tags
router = APIRouter(
    prefix=Shipment.prefix, tags=[Shipment.shipment]
)

# Define a FastAPI route to create a shipment order
@router.post("/shipment", response_model=Success)
async def create_shipment_order(
    order_data: ShipmentOrder, current_user: DBUser = Depends(get_current_user)
):
    # Convert ShipmentOrder data to a dictionary
    order_data = order_data.dict()
    # Check if the current user has the required role to create a shipment order
    check_role_access(current_user.role, [Roles.manager, Roles.client])
    # Check the company and/or warehouse associated with the order
    await check_order_company_and_or_warehouse(
        {"company_name": order_data["company_name"]}
    )
    # Add client-related data to the order
    order_data["client_id"]= current_user.id
    order_data["client_email"] = current_user.email
    order_data["first_name"] = current_user.firstname
    order_data["last_name"] = current_user.lastname
    order_data["telephone"] = current_user.telephone
    # Create the shipment order using the service function
    res = await create_shipment(order_data)
    return res

# Define a FastAPI route to retrieve all shipment orders
@router.get("/shipment/orders", response_model=Page[ShipmentOrderWithID])
async def get_all_shipment(current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role to retrieve shipment orders
    check_role_access(current_user.role, [Roles.manager, Roles.client])
    query = {}
    if current_user.role == Roles.manager:
        query = {}
    elif current_user.role == Roles.client:
        query = {"client_email": current_user.email}
    # Get all shipment orders based on the query
    order_data = await get_all_orders(query=query)
    # Paginate and return the results
    return paginate(order_data)

# Define a FastAPI route to retrieve a specific shipment order by its ID
@router.get("/{order_id}/shipment", response_model=dict)
async def get_order_of_shipment(order_id: str):
    # Get the shipment order by its ID
    order_data = await get_shipment_order_by_id(order_id)
    return order_data

# Define a FastAPI route to delete a shipment order by its ID
@router.delete("/{order_id}", response_model=dict)
async def delete_shipment_order(order_id: str, current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role to delete a shipment order
    check_role_access(current_user.role, [Roles.manager, Roles.client])
    query = {}
    if current_user.role == Roles.manager:
        query = {"_id": ObjectId(order_id)}
    elif current_user.role == Roles.client:
        query = {"_id": ObjectId(order_id), "client_email": current_user.email}
    # Attempt to delete the shipment order
    try:
        await delete_shipment_order_by_id(query)
    except Exception as e:
        raise e
    return {"success": "shipment_order successfully deleted"}

# Define a FastAPI route to update a shipment order by its ID
@router.put("/{order_id}", response_model=dict)
async def update_shipment_order(
    order_id: str, 
    shipment_data: Update_Shipment_order, 
    current_user: DBUser = Depends(get_current_user)
):
    try:
        # Check if the current user has the required role to update a shipment order
        check_role_access(current_user.role, [Roles.manager, Roles.client])
        shipment_data.validate_shipped_date(shipment_data.shipped_date)
        # Convert Update_Shipment_order data to a dictionary
        shipment_data = shipment_data.dict()    
        # Filter out None and "string" values from the shipment_data
        for key, val in shipment_data.items():
            if val is not None and val != "string":
                shipment_data[key] = val
        # Update the shipment order using the service function
        await update_shipment_order_by_id(order_id=order_id, order_data=shipment_data)
    except ValueError as e:
        # Обработка ошибки валидации
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise e
    return {"success": "shipment_order updated successfully"}

@router.put("/notify/team/{order_id}",response_model=dict)
async def notify_team_of_status_change(order_id:str,
                                       current_user:DBUser=Depends(get_current_user)):
    check_role_access(current_user.role,[Roles.admin,Roles.manager])
    order_data = await get_shipment_order_by_id(order_id=order_id)
    company_data = await get_company(name=current_user.company)
    order_data["status"]="approved"
    data ={
        "order_id":order_data["id"],
        "status":"Available with Restrictions"
    }
    for user in order_data["warehouse_team"]:
        await update_user_order_status(user["id"],data)
        data["description"]="There's a time change on this order, you can do another job"
        await manager.send_message(user["id"],str(data))
        email_data ={
            "office_email":company_data["office_email"],
            # "office_password":company_data["office_password"],
            "order_id":order_id,
            "recipient_email":user["email"],
            "description" : "There's a time change on this order, you can do another job",
            "subject":"Order Confirmation",
        }
        await send_email_to_client(email_data=email_data)
    await update_shipment_order_by_id(order_id=order_id,order_data=order_data)
    # await update_order(order_id=order_id,data=order_data)
    notification_datetime = datetime.combine(datetime.today(), order_data["last_notification_time"].time()) - timedelta(days=2)
    notification_datetime = notification_datetime.time()
    # Создайте задачу по расписанию
    scheduler.add_job(
        send_email_to_client,  # Передаем ссылку на функцию
        args=[email_data],  # Передаем аргументы в виде списка
        trigger=IntervalTrigger(minutes=30),
        max_instances=1,
        start_date=notification_datetime,
        end_date=order_data["last_notification_time"].time(),
        id=f"order_{order_id}_notification"
    )
    return {"success":"Information about the order has been communicated to everyone"}

# Add pagination support to the router
add_pagination(router)
