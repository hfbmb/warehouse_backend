from pydantic import BaseModel,Field,validator
from typing import List,Optional
from datetime import datetime,timedelta


class Warehouse(BaseModel):
    warehouse_name: str = Field(
        ..., description="warehouse name", min_length=1, max_length=100
    )
    street: str = Field(
        ..., description="Street of company location", min_length=1, max_length=100
    )
    city: str = Field(
        ..., description="City of company location", min_length=1, max_length=100
    )
    region: str = Field(
        ..., description="Region of company location", min_length=1, max_length=50
    )
    country: str = Field(
        ..., description="Country of company lfocation", min_length=1, max_length=50
    )
    class Config:
        json_schema_extra ={
            "example":{
                "warehouse_name": "warehouse1",
                "street": "123 Main Street",
                "city": "Cityville",
                "region": "Regionville",
                "country": "Countryland"
            }
        }



class Gate(BaseModel):
    gate_name :str = Field(None,description="gate name of warehouse")
    class Config:
        json_schema_extra={
            "example":{
                "gate_name":"gate1",
            }
        }

class UpdateWarehouse(BaseModel):
    # warehouse_name: str = Field(None, description="warehouse name")
    street: str = Field(None, description="Street of company location")
    city: str = Field(None, description="City of company location")
    region: str = Field(None, description="Region of company location")
    country: str = Field(None, description="Country of company lfocation")
    gates: List[Gate] = Field(None, description="List of gate")

    class Config:
        json_schema_extra ={
            "example":{
                # "warehouse_name": "Updated Warehouse",
                "street": "456 Elm Street",
                "city": "New City",
                "region": "New Region",
                "country": "New Country",
                "gates": [
                    {
                        "gate_number": "Gate 1",
                    },
                    {
                        "gate_number": "Gate 2",
                    }
                ]
            }
        }


class Category(BaseModel):
    category_name : str = Field(...,description="the category name of warehouse",min_length=1,max_length=50)
    # category_price:float =Field(default=1,description="the category price")
    category_time : int = Field(...,description="the category time of warehouse")
    category_price : float = Field(...,description="category price on the time")
    created_at : datetime = Field(default=datetime.now(),description="created this post")
    warehouse_id : str = Field(...,description="the warehouse id")

    class Config:
        json_schema_extra ={
            "example":{
                "category_name": "Electronics",
                "category_time": 5,
                "category_price": 10.99,
                "created_at": "2023-10-18T12:34:56",
                "warehouse_id": "warehouse123"
            }
        }

class CategoryUpdate(BaseModel):
    category_name : str = Field(None,description="the category name of warehouse")
    # category_price:float =Field(default=None,description="the category price")
    category_time : int = Field(None,description="the category time of warehouse")
    category_price : float = Field(None,description="category price on the time")
    updated_at : datetime = Field(default=datetime.now(),description="created this post")
    warehouse_id : str = Field(None,description="the warehouse id")

    class Config:
        json_schema_extra ={
            "example":{
                "category_name": "Clothing",
                "category_time": 3,
                "category_price": 7.99,
                "updated_at": "2023-10-19T08:45:30",
                "warehouse_id": "warehouse456"
            }
        }



class Zones (BaseModel):
    zone_name : str = Field(...,description="zone name",min_length=1)
    category_id : str = Field(...,description="the id of category")
    created_at : datetime = Field(default=datetime.now(),description="created this port")
    zone_price : float = Field(default=1,description="zone price")

    class Config:
        json_schema_extra ={
            "example":{
                "zone_name": "Zone A",
                "category_id": "category123",
                "created_at": "2023-10-19T10:15:30",
                "zone_price": 2.99
            }
        }
class ZoneById(Zones):
    id : str = Field(...,description="zone with id")
    class Config:
        json_schema_extra ={
            "example":{
                "zone_name": "Zone A",
                "category_id": "category123",
                "created_at": "2023-10-19T10:15:30",
                "zone_price": 2.99,
                "id":"123ads3",
            }
        }
    
class ZoneUpdate(BaseModel):
    zone_name : str = Field(None,description="zone name")
    zone_price:float = Field(default=None,description="zone price ==0")
    category_id : str = Field(None,description="the id of category")
    updated_at : datetime = Field(default=datetime.now(),description="created this port")

    class Config:
        json_schema_extra ={
            "example":{
                "zone_name": "Updated Zone A",
                "zone_price": 0.0,
                "category_id": "category123",
                "updated_at": "2023-10-19T15:45:00"
            }
        }

class Condition(BaseModel):
    condition_name : str = Field(...,description="condition name",min_length=1)
    condition_start : int = Field(...,description="condition start at",ge=1)
    condition_end : int = Field(default=3,description="end time of conditon")
    condition_status: bool = Field(default=False,description="status of condition")
    condition_price : float = Field(...,description="the condition price")
    zone_id : str = Field(...,description="zone of id")
    created_at :datetime = Field(default=datetime.now(),description="created time")

    class Config:
        json_schema_extra ={
            "example":{
                "condition_name": "Sample",
                "condition_start": 1,
                "condition_price": 9.99,
                "zone_id": "A123"
            }
        }
class ConditionUpdate(BaseModel):
    condition_name : str = Field(None,description="condition name")
    condition_start : int = Field(None,description="condition start at",ge=1)
    condition_end : int = Field(None,description="end time of conditon")
    condition_status: bool = Field(default=False,description="status of condition")
    condition_price : float = Field(None,description="the condition price")
    zone_id : str = Field(None,description="zone of id")
    updated_at : datetime = Field(default=datetime.now(),description="updated time")

    class Config:
        json_schema_extra ={
            "example": {
                "condition_name": "Updated Condition",
                "condition_start": 3,
                "condition_end": 6,
                "condition_status": True,
                "condition_price": 19.99,
                "zone_id": "Zone123",
                # "updated_at":None,  # Specify a custom updated time
            }
        }


class Racks(BaseModel):
    rack_name : str = Field(...,description="name of rack",min_length=1)
    rack_quantity :int = Field(default=1,description="rack quantity")
    rack_price : int = Field(default=1,description="price of rack")
    rack_length : float = Field(...,description="length of rack")
    rack_width : float  = Field(...,description="rack width")
    rack_height : float = Field(...,description="height of rack")
    zone_id : str = Field(...,description="zone of id")
    # conditions : List[Optional(ConditionForRack)]=Field(None,description="rack conditions")
    created_at:datetime = Field(default=datetime.now(),description="created at time")

    class Config:
        json_schema_extra = {
            "example": {
                "rack_name": "Sample Rack",
                "rack_quantity": 5,
                "rack_price": 200,
                "rack_length": 8.5,
                "rack_width": 1.2,
                "rack_height": 10.0,
                "zone_id": "Zone456",
                # "created_at": None,  # Specify a custom created time
            }
        }

class RackUpdate(BaseModel):
    rack_name : str = Field(None,description="name of rack")
    rack_quantity :int = Field(default=None,description="rack quantity")
    rack_price : int = Field(default=None,description="price of rack")
    rack_length : float = Field(None,description="length of rack")
    rack_width : float  = Field(None,description="rack width")
    rack_height : float = Field(None,description="height of rack")
    zone_id : str = Field(None,description="zone of id")
    # conditions : List[Optional(ConditionForRack)]=Field(None,description="rack conditions")
    updated_at:datetime = Field(default=datetime.now(),description="created at time")

    class Config:
        json_schema_extra = {
            "example": {
                "rack_name": "Updated Rack",
                "rack_quantity": 3,
                "rack_price": 150,
                "rack_length": 8.0,
                "rack_width": 1.8,
                "rack_height": 10.5,
                "zone_id": "Zone789",
                # "updated_at": None,  # Specify a custom updated time
            }
        }


class Floors(BaseModel):
    floor_name : str = Field(...,description="floor number",min_length=1)
    floor_quantity : int = Field(default=1,description="floor quantity")
    floor_length : float = Field(default=None,description= "default it's equal to rack_length")
    floor_height : float = Field(default=1,description="floor height")
    floor_width : float = Field(default=None,description="default equal to rack_width")
    floor_weight : float = Field(default=100,description="floor weight of floor")
    floor_max_price : float = Field(default=100,description="floor max price")
    floor_price_percent : float = Field(default=5,description="price of floor")
    rack_id : str = Field(...,description="rack of id")
    created_at : datetime = Field(default=datetime.now(),description="created_at floor")

    class Config:
        json_schema_extra ={
            "example":{
                "floor_name": "Floor1",
                "floor_quantity": 2,
                "floor_length": 5.5,
                "floor_height": 1.5,
                "floor_width": 1.0,
                "floor_weight": 200.0,
                "floor_max_price": 250.0,
                "floor_price_percent": 7.5,
                "rack_id": "Rack123"
            }
        }

class FloorUpdate(BaseModel):
    loor_name : str = Field(None,description="floor number")
    floor_quantity : int = Field(default=None,description="floor quantity")
    floor_length : float = Field(default=None,description= "default it's equal to rack_length")
    floor_height : float = Field(default=None,description="floor height")
    floor_width : float = Field(default=None,description="default equal to rack_width")
    floor_weight : float = Field(default=None,description="floor weight of floor")
    floor_price_percent : float = Field(None,description="price of floor")
    rack_id : str = Field(None,description="rack of id")
    updated_at : datetime = Field(default=datetime.now(),description="created_at floor")

    class Config:
        json_schema_extra ={
            "example":{
                "floor_name": "Updated Floor1",
                "floor_quantity": 3,
                "floor_length": 6.0,
                "floor_height": 1.5,
                "floor_width": 1.5,
                "floor_weight": 250.0,
                "floor_price_percent": 8.0,
                "rack_id": "UpdatedRack123"
            }
        }

class Cells(BaseModel):
    cell_name : str = Field(...,description="cell_name of cell")
    cell_quantity : int = Field(default=1,description="cell_quantity")
    cell_length : float = Field(default=None,description= "default it's equal to floor_length")
    cell_height : float = Field(default=1,description="default it's equal to floor height")
    cell_width : float = Field(default=None,description="default equal to floor_width")
    cell_weight : float = Field(default=100,description="default equal to floor_weight")
    cell_price : float = Field(...,description="default equal to all summa of process")
    status :str =Field(default="active",description="status of cell")
    floor_id : str = Field(default=1,description="floor id")
    created_at : datetime = Field(default=datetime.now(),description="created at")

    class Config:
        json_schema_extra ={
            "example":{
                "cell_name": "CellA",
                "cell_quantity": 2,
                "cell_length": 1.5,
                "cell_height": 0.8,
                "cell_width": 1.0,
                "cell_weight": 50.0,
                "cell_price": 75.0,
                "status": "active",
                "floor_id": "Floor456"
            }
        }

class CellUpdate(BaseModel):
    cell_name : str = Field(None,description="cell_name of cell")
    cell_quantity : int = Field(None,description="cell_quantity")
    cell_length : float = Field(default=None,description= "default it's equal to floor_length")
    cell_height : float = Field(default=None,description="default it's equal to floor height")
    cell_width : float = Field(default=None,description="default equal to floor_width")
    cell_weight : float = Field(default=None,description="default equal to floor_weight")
    cell_price : float = Field(None,description="default equal to all summa of process")
    floor_id : str = Field(None,description="floor id")
    status :str =Field(default=None,description="status of cell")
    updated_at : datetime = Field(default=datetime.now(),description="created at")

    class Config:
        json_schema_extra ={
            "example":{
                "cell_name": "UpdatedCellA",
                "cell_quantity": 3,
                "cell_length": 1.8,
                "cell_height": 1.0,
                "cell_width": 1.0,
                "cell_weight": 60.0,
                "cell_price": 80.0,
                "status": "inactive",
                "floor_id": "UpdatedFloor456"
            }
        }
    


class Boxes(BaseModel):
    box_type_id : str = Field(...,description="type id of box")
    box_quantity : int = Field(default=1,description="box quantity",ge=1)
    box_weight : float = Field(default=5,description="box weight")
    box_address: str = Field(default="outside",description="it will be save here cell_id")
    box_products : Optional[list]=Field(default=[],description="product details")

    class Config:
        json_schema_extra ={
            "example":{
                "box_type_id":"1232qwe",
                "box_quantity":123,
                "box_weight":123,
                "box_address":"outside"
            }
        }


class BoxesUpdate(BaseModel):
    box_type_id : str = Field(None,description="type id of box")
    box_quantity : int = Field(default=None,description="box quantity")
    box_weight : float = Field(default=None,description="box weight")
    box_address: str = Field(default=None,description="it will be save here cell_id")
    box_products : Optional[list]=Field(default=None,description="product details")


class TypeBox(BaseModel):
    type_name : str = Field(default="small",description="type name")
    type_height : float = Field(default=5,description="height of box")
    type_length : float = Field(default=3,description="length of type")
    type_width : float = Field(default=2,description="width of type")
    type_status : str = Field(default="small",description="status of box")

    class Config:
        json_schema_extra ={
            "example":{
                "type_name":"small",
                "type_height":10,
                "type_length":12,
                "type_width":11,
                "type_status":"active"
            }
        }


class UpdateTypeBox(BaseModel):
    type_name : str = Field(default=None,description="type name")
    type_height : float = Field(default=None,description="height of type")
    type_lengtn : float = Field(default=None,description="length of type")
    type_width : float = Field(default=None,description="width of type")
    type_status : str = Field(default=None,description="status of type")
