from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from ..user.models import UserWithID
from datetime import datetime

class ConditionID(BaseModel):
    condition_id : str = Field(...,description="condition id")
    class Config:
        json_schema_extra ={
            "example":{
                "condition_id":"1w335450juer4",
            }
        }

class ClientSideProduct(BaseModel):
    product_name: str = Field(
        ..., description="name of the product", min_length=1, max_length=100
    )
    quantity: int = Field(
        ..., description="quantity of a certain product", ge=1, le=100000
    )
    price: float = Field(None, description="price of a certain product", ge=0)
    conditions : Optional[List[ConditionID]]=Field(default=None,description="product need condition")
    serial_number: str = Field(
        ..., description="serial_number of product", min_length=1, max_length=50
    )
    # tags: Optional[list] = Field(None, description='category tags of a certain product')
    weight: float = Field(
        ..., description="weight of a certain product", ge=0.01, le=10000
    )
    expiration_date: Optional[float] = Field(
        default=None, description="expiration date product"
    )
    box_type_id : str = Field(...,description="box type id")
    storing_duration : float = Field(default=10,description="storing duration in warehouse type=min")
    height: int = Field(..., description="Height of a product", ge=1, le=1000000)
    width: int = Field(..., description="Width of a product", ge=1, le=1000000)
    length: int = Field(..., description="Length of a product", ge=1, le=1000000)
    # booking_date: float = Field(..., description='when a product should be delivered to client')
    packing_type: str = Field(
        ...,
        description="product may come in different packages: pallets, crates etc.",
        min_length=1,
        max_length=50,
    )
    dimension_type: str = Field(
        ..., description="Dimension type", min_length=1, max_length=50
    )
    weight_type: str = Field(
        ..., description="Weight type", min_length=1, max_length=50
    )

    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "product_name",
                "quantity": 1,
                "price": 0.0,
                "conditions":[
                    {"condition_id":"asdsa213"},
                    {"condtion_id":"213123123"}
                ],
                "weight": 1.1,
                "box_type_id":"123",
                "height": 1,
                "width": 1,
                "length": 1,
                "packing_type": "pallets",
                "dimension_type": "container",
                "weight_type": "container",
                "expiration_date": 1.1,
            }
        }
        extra = "allow"


class ManagerSideProduct(BaseModel):
    # schedule: float = Field(..., description="Schedule of unloading goods.")
    initial_schedule: str = Field(
        default=str(datetime.now().date().isoformat()),
        description="Start schedule of unloading goods",
    )
    end_schedule: str = Field(
        default=str(datetime.now().date().isoformat()),
        description="End schedule of unloading goods",
    )
    place: str = Field(..., description="Place of arrived transport. Number of entry.)")
    # time: float = Field(..., description="It can be duration of unloading goods or time when it starts.")
    initial_time: str = Field(
        default=str(datetime.now().time().isoformat()),
        description="Start time of unloading goods",
    )
    end_time: str = Field(
        default=str(datetime.now().time().isoformat()),
        description="End time of unloading goods",
    )

    warehouse_team: Optional[List[UserWithID]] = Field(
        None,
        description="a team of workers that should receive a product",
        min_items=1,
        max_items=100,
    )
    # responsible_workers: Optional[list] = Field(None, description='a team member, who has invoice data')

    @field_validator("initial_schedule", "end_schedule")
    @classmethod
    def validate_iso_format_date(cls, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid ISO 8601 format for date")
        return value

    @field_validator("initial_time", "end_time")
    @classmethod
    def validate_iso_format_time(cls, value):
        try:
            datetime.strptime(value, "%H:%M")
        except ValueError:
            raise ValueError("Invalid ISO 8601 format for time")
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "initial_schedule": "2023-08-08",
                "end_schedule": "2023-08-08",
                "place": 0,
                "initial_time": "09:10",
                "initial_end": "09:19",
                "warehouse_team": [""],
            }
        }

