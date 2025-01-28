import logging
import asyncio
from typing import List,Dict
from bson.objectid import ObjectId
# from ..exceptions import DoesNotExist
# from .models import 
from ..company.exception import CompanyNotFound
from ..database import (warehouses_collection,
                        zones_collection,
                        categories_collection,
                        racks_collection,
                        floors_collection,cells_collection,
                        conditions_collection,
                        boxes_collection,
                        types_collection)
from ..company import constants
from .exceptions import (WarehouseNotFound,
                         ZoneNotFound,FloorNotFound,
                         RackNotFound,CellNotFound,
                         CategoryNotFound,ConditionNotFound,
                         BoxNotFound,BoxNotFoundByid,BoxIsBusy)

# Function to add a new warehouse to a company
async def get_warehouse_by_id(id:str)->dict:
    warehouse = await warehouses_collection.find_one({"_id":ObjectId(id)})
    if warehouse:
        warehouse["id"]=str(warehouse.pop("_id"))
        return warehouse
    else:
        raise WarehouseNotFound

async def get_all_warehouses(query:dict)->list:
    warehouses = warehouses_collection.find(query)
    reslut =[]
    async for warehouse in warehouses:
        warehouse["id"]= str(warehouse.pop("_id"))
        reslut.append(warehouse)
    return reslut

async def create_warehouse(company_name: str, data: dict):
    data["company_name"]=company_name
    res =await warehouses_collection.insert_one(data)
    if res.inserted_id:
        pass
    else:
        raise Exception
    
async def check_warehouse_data_by_id(id:str):
    result = await warehouses_collection.find_one({"_id":ObjectId(id)})
    if result:
        pass 
    else:
        raise WarehouseNotFound

    
async def update_warehouse_data(query:dict,warehouse_data:dict):
    updated_data = await warehouses_collection.update_one(query,{"$set":warehouse_data})
    if updated_data.matched_count >1:
        pass
    else:
        raise WarehouseNotFound

# Function to retrieve the warehouse associated with the current user
async def current_user_warehouse(query: dict):
    result = await warehouses_collection.find_one(
        {
            constants.Company.company_name: query[constants.Company.company_name],
            constants.Warehouses.warehouse_name:query[constants.Warehouses.warehouse_name],
            constants.Company.deletionDate: {"$exists": False},
        }
    )
    if not result:
        logging.error("current_user_warehouse: Company not found")    
        raise WarehouseNotFound()
    result["id"]=str(result.pop("_id"))
    return result

# Function to delete a warehouse from a company's data
async def warehouse_delete(query: dict):
    deleted_result = await warehouses_collection.delete_one(query)
    if deleted_result.matched_count == 0:
        logging.error("warehouse_delete: Warehouse does not exist")
        raise WarehouseNotFound()
    else:
        pass


# Function to delete a gate by gate_name
async def delete_gate_by_gate_name(data: dict) -> dict:
    result = await warehouses_collection.update_one(
        {
            constants.Company.company_name: data["company_name"],
            "warehouse_name": data["warehouse_name"],
        },
        {"$pull": {"gates": {"gate_name": data["gate_name"]}}},
    )
    if result.modified_count > 0:
        return {"success": f"The gate {data['gate_name']} was removed successfully"}
    else:
        return {}

### This service functions for zones

# Create a new zone with the provided data.
async def create_zone(data: dict):
    category_data = await get_category_by_id(id=data["category_id"])
    data["zone_price"]+=category_data["category_price"]
    result = await zones_collection.insert_one(data)
    if result.inserted_id:
        pass  # Success
    else:
        raise Exception  # Raise an exception if insertion fails

# Check the existence of a zone by its ID.
async def check_zone_by_id(id: str):
    res = await zones_collection.find_one({"_id": ObjectId(id)})
    if res:
        pass  # Zone found
    else:
        raise ZoneNotFound  # Raise an exception if the zone is not found

# Update a zone with the given query and data.
async def update_zone(query: dict, data: dict):
    result = await zones_collection.update_one(query, {"$set": data})
    if result.matched_count > 0:
        pass  # Success
    else:
        raise ZoneNotFound  # Raise an exception if no matching zone is found

# Delete a zone with the specified query.
async def delete_zone(query: dict):
    result = await zones_collection.delete_one(query)
    if result.deleted_count > 0:
        pass  # Success
    else:
        raise ZoneNotFound  # Raise an exception if no zone is deleted

# Get a zone by its ID.
async def get_zone_by_id(query: dict):
    result = await zones_collection.find_one(query)
    if not result:
        raise ZoneNotFound  # Raise an exception if the zone is not found
    result["id"] = str(result.pop("_id"))
    return result

# Get all zones that match the provided query.
async def get_all_zones(query: dict) -> []:
    result = zones_collection.find(query)
    res = []
    async for zone in result:
        zone["id"] = str(zone.pop("_id"))
        res.append(zone)
    return res

### This functions for categories

# Check the existence of a category by its ID.
async def check_category_by_id(id: str):
    result = await categories_collection.find_one({"_id": ObjectId(id)})
    if result:
        pass  # Category found
    else:
        raise CategoryNotFound  # Raise an exception if the category is not found

# Create a new category with the provided data.
async def create_category(data: dict):
    result = await categories_collection.insert_one(data)
    if result.inserted_id:
        pass  # Success
    else:
        raise CategoryNotFound  # Raise an exception if insertion fails

# Get a category by its ID.
async def get_category_by_id(id: str):
    result = await categories_collection.find_one({"_id": ObjectId(id)})
    if result:
        result["id"] = str(result.pop("_id"))
        return result
    else:
        raise CategoryNotFound  # Raise an exception if the category is not found

# Get all categories that match the provided query.
async def get_all_categories(query: dict) -> []:
    results = categories_collection.find(query)
    if not results:
        raise CategoryNotFound  # Raise an exception if no categories are found
    res = []
    async for cat in results:
        cat["id"] = str(cat.pop("_id"))
        res.append(cat)
    return res

# Update a category with the given query and data.
async def update_category(query: dict, data: dict):
    result = await categories_collection.update_one(query, {"$set": data})
    if result.matched_count > 0:
        pass  # Success
    else:
        raise CategoryNotFound  # Raise an exception if no matching category is found

async def delete_category_by_id(id:str):
    res = await categories_collection.delete_one({"_id":ObjectId(id)})
    if res.deleted_count>0:
        pass
    else:
        raise CategoryNotFound


### This service functions for condition

# Create a new condition with the provided data.
async def create_condition(data: dict):
    result = await conditions_collection.insert_one(data)
    if not result.inserted_id:
        raise Exception  # Raise an exception if insertion fails
    else:
        query ={"_id":ObjectId(data["zone_id"])}
        zone_data = await get_zone_by_id(query=query)
        zone_data["zone_price"]+=data["condition_price"]
        await update_zone(query=query,data=zone_data)
        pass

# Check the existence of a condition by its ID.
async def check_condition_by_id(id: str):
    result = await conditions_collection.find_one({"_id": ObjectId(id)})
    if result:
        pass  # Condition found
    else:
        raise ConditionNotFound  # Raise an exception if the condition is not found

# Get a condition by its ID.
async def get_condition_by_id(id: str) -> dict:
    result = await conditions_collection.find_one({"_id": ObjectId(id)})
    if not result:
        raise ConditionNotFound  # Raise an exception if the condition is not found
    result["id"] = str(result.pop("_id"))
    return result

# Get all conditions that match the provided query.
async def get_all_conditions(query: dict):
    results = conditions_collection.find(query)
    res = []
    async for cat in results:
        cat["id"] = str(cat.pop("_id"))
        res.append(cat)
    return res

async def delete_condition_by_qurey(query:dict):
    res = await conditions_collection.delete_one(query)
    if res.deleted_count>0:
        pass
    else:
        raise ConditionNotFound

# Update conditions with the given query and data.
async def update_conditions(query: dict, data: dict):
    result = await conditions_collection.update_one(query, {"$set": data})
    if not result:
        raise ConditionNotFound  # Raise an exception if no matching condition is found
    else:
        pass  # Success

### This service functions for racks

# Create racks based on the provided data. Calculate prices for each rack based on conditions.
async def create_rack(data: Dict):
    racks = []
    for _ in range(data["rack_quantity"]):
        racks.append(data)

    result = racks_collection.insert_many(racks)
    if not result:
        raise Exception("Failed to insert data")
    else:
        pass  # Success

# Check the existence of a rack by its ID.
async def check_rack_by_id(id: str):
    result = await racks_collection.find_one({"_id": ObjectId(id)})
    if result:
        pass  # Rack found
    else:
        raise RackNotFound  # Raise an exception if the rack is not found

# Get a rack by its ID.
async def get_rack_by_id(id: str) -> dict:
    result = await racks_collection.find_one({"_id": ObjectId(id)})
    if not result:
        raise RackNotFound  # Raise an exception if the rack is not found
    result["id"] = str(result.pop("_id"))
    return result

# Get all racks that match the provided query.
async def get_all_racks(query: dict):
    results = racks_collection.find(query)
    res = []
    async for cat in results:
        cat["id"] = str(cat.pop("_id"))
        res.append(cat)
    return res

# Update racks with the given query and data.
async def update_racks(query: dict, data: dict):
    result = await racks_collection.update_one(query, {"$set": data})
    if not result:
        raise RackNotFound  # Raise an exception if no matching rack is found
    else:
        pass  # Success


#delete rack by id
async def delete_rack_by_id(id:str):
    res = await racks_collection.delete_one({"_id":ObjectId(id)})
    if res.deleted_count>0:
        pass
    else:
        raise RackNotFound

### This service functions for floors

# Create multiple floors based on the provided data.
async def create_floor(data: dict):
    floors = []
    floor_max_price = data["floor_max_price"]  # Initialize the floor_max_price
    for _ in range(data["floor_quantity"]):
        # Create a new dictionary for each floor based on the original data
        floor_data = data.copy()  # Create a copy of the original data
        floor_data["floor_max_price"] = floor_max_price  # Set the current floor_max_price
        floors.append(floor_data)

        # Reduce floor_max_price for the next floor
        floor_max_price -= floor_max_price * (data["floor_price_percent"] / 100)

    result = floors_collection.insert_many(floors)
    if result:
        pass  # Success
    else:
        raise Exception("Failed to insert data")
 # Raise an exception if insertion fails

# Check the existence of a floor by its ID.
async def check_floor_by_id(id: str):
    result = await floors_collection.find_one({"_id": ObjectId(id)})
    if result:
        pass  # Floor found
    else:
        raise FloorNotFound  # Raise an exception if the floor is not found

# Get a floor by its ID.
async def get_floor_by_id(id: str) -> dict:
    result = await floors_collection.find_one({"_id": ObjectId(id)})
    if not result:
        raise FloorNotFound  # Raise an exception if the floor is not found
    result["id"] = str(result.pop("_id"))
    return result

# Get all floors that match the provided query.
async def get_all_floors(query: dict):
    results = floors_collection.find(query).sort([("created_at", -1)])
    res = []
    async for cat in results:
        cat["id"] = str(cat.pop("_id"))
        res.append(cat)
    return res

# Update floors with the given query and data.
async def update_floors(query: dict, data: dict):
    result = await floors_collection.update_one(query, {"$set": data})
    if not result:
        raise FloorNotFound  # Raise an exception if no matching floor is found
    else:
        pass  # Success

async def delete_floor_by_id(id:str):
    res = await floors_collection.delete_one({"_id":ObjectId(id)})
    if res.deleted_count>0:
        pass
    else:
        raise FloorNotFound

### This service functions for cells

# Create multiple cells based on the provided data.
async def create_cell(data: dict):
    cells = []
    for _ in range(data["cell_quantity"]):
        # data.pop("cell_quantity")
        cell_data=data.copy()
        cells.append(cell_data)

    result = cells_collection.insert_many(cells)
    if result:
        pass  # Success
    else:
        raise Exception("Failed to insert data")  # Raise an exception if insertion fails

# Check the existence of a cell by its ID.
async def check_cell_by_id(id: str):
    result = await cells_collection.find_one({"_id": ObjectId(id)})
    if result:
        pass  # Cell found
    else:
        raise CellNotFound  # Raise an exception if the cell is not found

# Get a cell by its ID.
async def get_cell_by_id(id: str) -> dict:
    result = await cells_collection.find_one({"_id": ObjectId(id)})
    if not result:
        raise CellNotFound  # Raise an exception if the cell is not found
    result["id"] = str(result.pop("_id"))
    return result

# Get all cells that match the provided query.
async def get_all_cells(query: dict)->list:
    results = cells_collection.find(query)
    res = []
    async for cat in results:
        cat["id"] = str(cat.pop("_id"))
        res.append(cat)
    return res

# Update cells with the given query and data.
async def update_cells(query: dict, data: dict):
    result = await cells_collection.update_one(query, {"$set": data})
    if not result:
        raise CellNotFound  # Raise an exception if no matching cell is found
    else:
        pass  # Success

async def delete_cell_by_id(id:str):
    res = await cells_collection.delete_one({"_id":ObjectId(id)})
    if res.deleted_count>0:
        pass
    else:
        raise CellNotFound

###All functions for box
async def create_box_for_cell(data:dict):
    boxes =[]
    for _ in range(data["box_quantity"]):
        box_data = data.copy()
        boxes.append(box_data)
    result = boxes_collection.insert_many(boxes)
    if result:
        pass 
    else:
        raise Exception("Failed to insert data")

async def get_box_data_by_id(id:str):
    box_data = await boxes_collection.find_one({"_id":ObjectId(id)})
    if box_data:
        box_data["id"]= str(box_data.pop("_id"))
        return box_data
    else:
        raise BoxNotFoundByid

async def get_all_boxes_data(query:dict):
    boxes =[]
    result = boxes_collection.find(query).sort({"volume":1})
    async for box in result:
        box["id"]= str(box.pop("_id"))
        boxes.append(box)
    return boxes

async def update_box_data(query:dict,data:dict):
    result =await boxes_collection.update_one(query,{"$set":data})
    if result:
        pass
    else:
        raise BoxNotFound

async def delete_box_by_id(id:str):
    res = await boxes_collection.delete_one({"_id":ObjectId(id)})
    if res.deleted_count>0:
        pass
    else:
        raise BoxNotFoundByid

#####All box_type functions
async def create_box_type_data(data:dict):
    result =await types_collection.insert_one(data)
    if result:
        pass
    else:
        raise Exception("error in the create box type function")

async def get_box_type_data_by_id(id:str)->dict:
    result = await types_collection.find_one({"_id":ObjectId(id)})
    if result:
        result["id"]=str(result.pop("_id"))
        return result
    else:
        raise BoxNotFoundByid

async def get_all_box_type_data(query:dict)->list:
    try:
        boxes =[]
        result = types_collection.find(query).sort({"volume":1})
        async for box in result:
            box["id"]=str(box.pop("_id"))
            boxes.append(box)
        return boxes
    except Exception as e:
        raise e
    
async def update_box_type_data(query:dict,data:dict):
    result = await types_collection.update_one(query,{"$set":data})
    if result.matched_count >0:
        pass
    else:
        raise BoxNotFound

async def delete_box_type_data_by_id(id:str):
    res = await types_collection.delete_one({"_id":ObjectId(id)})
    if res.deleted_count>0:
        pass
    else:
        raise BoxNotFoundByid
##### put_product_in_the_cell
# This function finds an appropriate cell in a warehouse to place a product based on various criteria.

async def get_product_warehouse_category(query: dict, product_data: dict) -> dict:
    # Retrieve warehouse data based on the provided query.
    warehouse_data = await warehouses_collection.find_one(query)
    # Get all categories in the warehouse.
    product_data["warehouse_id"]=str(warehouse_data["_id"])
    categories = await get_all_categories(query={"warehouse_id": str(warehouse_data["_id"])})
    # Initialize variables to track zone and rack status.
    zone_status = False
    rack_status = False
    # Iterate through categories to find the suitable one.
    for category in categories:
        # Check if the category's time is greater than or equal to the product's storing duration.
        if category["category_time"] >= product_data["storing_duration"]:
            # Assign the category ID to the product and store category data.
            product_data["category_id"] = category["id"]
            # Get all zones within the selected category.
            zones =await get_all_zones({"category_id": category["id"]})
            # Iterate through zones to find a suitable one.
            for zone in zones:
                if product_data["conditions"]==None:
                    zone_status=True
                    product_data["zone_id"] = zone["id"]
                    break
                # Get conditions for the zone.
                conditions = await get_all_conditions({"zone_id": zone["id"]})
                if all(condition["condition_id"] in [c["condition_id"] for c in conditions] for condition in product_data["conditions"]):
                    product_data["zone_id"] = zone["id"]
                    zone_status=True
                    break
                # Iterate through conditions to find a matching one.
                if zone_status:
                    break
            if zone_status:
                break
    # Get all racks within the selected zone.
    racks = await get_all_racks({"zone_id": product_data["zone_id"]})
    # Iterate through racks to find a suitable one.
    for rack in racks:
        # Get all floors within the rack.
        floors = await get_all_floors({"rack_id": rack["id"]})
        # Iterate through floors to find a suitable one.
        for floor in floors:
            # Get all cells within the floor.
            cells = await get_all_cells({"floor_id": floor["id"]})
            # Iterate through cells to find an active cell with sufficient volume and weight capacity.
            for cell in cells:
                cell["status"]="active"
                if cell["status"]=="active" and cell["cell_volume"] >= product_data["volume"] and cell["cell_weight"] >= product_data["weight"]:
                    rack_status = True
                    product_data["cell_id"] = cell["id"]
                    product_data["floor_id"] = floor["id"]
                    product_data["rack_id"] = rack["id"]    
                    # Update the cell's volume, weight, and add the product to its list.
                    cell["cell_percent"]=(product_data["volume"]/ cell["cell_volume"] )* 100
                    cell["cell_volume"] -= product_data["volume"]
                    cell["cell_weight"] -= product_data["weight"]
                    cell["status"]="inwaiting"
                    cell["products"].append(product_data)      
                    # Update the cell in the database.
                    await update_cells({"_id": ObjectId(cell["id"])}, cell)
                    break
            if rack_status:
                break
    return product_data


async def storage_product_to_box(product_data:dict):
    boxes = await get_all_boxes_data(query={"box_type_id":product_data["box_type_id"]})
    product_data["boxes"]=[]
    for box in boxes:
        if (box["length"]>=product_data["length"]
             and box["width"]>=product_data["width"]
             and box["height"]>=product_data["height"]):
            min_quantity =product_data["quantity"]- box["height"]//product_data["height"]
            if min_quantity ==0:
                product_data["boxes"].append(box["id"])
                box["products"]=[].append(product_data)
                box["status"]="inbox"
                await update_box_data({"_id":ObjectId(box["id"])})
                break
            else:
                product_data["quantity"]=min_quantity
                continue
    return product_data


async def boxes_with_product(data:dict):
    # boxes_status = await get_all_boxes_data()
    count =0
    for box in data["boxes"]:
        box_data = await get_box_data_by_id(id=box["id"])
        if box_data["status"] =="active":
            count +=1
    
    if count != len(data["boxes"]):
        raise BoxIsBusy
    for box in data["boxes"]: 
        await update_box_data(query={"_id":ObjectId(box["id"])},data=box)
    



