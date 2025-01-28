# Installed packages
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from fastapi import UploadFile

# Local packages
from ..user.models import UserWithID


class Invoice(BaseModel):
    name: str = Field(
        ..., description="name of the product", min_length=1, max_length=100
    )
    quantity: int = Field(
        ..., description="quantity of a certain product", ge=1, le=1000000
    )
    price: float = Field(..., description="price of a number", ge=0)
    tags: Optional[List] = Field(None, description="category tags of a product")
    weight: float = Field(
        ..., description="weight of a certain product", ge=0.01, le=100000
    )
    height: int = Field(..., description="Height of a product", ge=1, le=100000)
    width: int = Field(..., description="Width of a product", ge=1, le=100000)
    length: int = Field(..., description="Length of a product", ge=1, le=100000)
    booking_date: float = Field(..., description="when a product should arrive")
    packing_type: str = Field(
        ...,
        description="product may come in different packages: pallets, crates etc.",
        min_length=3,
        max_length=50,
    )
    initial_schedule: str = Field(
        default=str(datetime.now().date().isoformat()),
        description="Start schedule of unloading goods",
    )
    end_schedule: str = Field(
        default=str(datetime.now().date().isoformat()),
        description="End schedule of unloading goods",
    )
    place: int = Field(..., description="a place where product should delivered")
    initial_time: str = Field(
        default=str(datetime.now().date().isoformat()),
        description="Start time of unloading goods",
    )
    end_time: str = Field(
        default=str(datetime.now().date().isoformat()),
        description="End time of unloading goods",
    )
    warehouse_team: List[UserWithID] = Field(
        ...,
        description="a team of workers that should receive a product",
        max_items=100,
    )
    responsible_worker: Optional[str] = Field(
        None, description="a team member, who has invoice data"
    )
    status: str = Field(..., description="status of a product's current stage")

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
            datetime.strptime(value, "%H:%M:%S.%f")
        except ValueError:
            raise ValueError("Invalid ISO 8601 format for time")
        return value


class ProductArrival(BaseModel):  # Dispatcher Side Report
    order_id: str = Field(..., description="order id", min_length=1, max_length=100)
    product_id: str = Field(
        ..., description="id of product", min_length=1, max_length=100
    )
    product_name: str = Field(
        ..., description="product name", min_length=1, max_length=100
    )
    quantity: int = Field(..., description="quantity of one product", ge=1, le=10000)
    # date_of_arrival: float = Field(..., description="when a product was delivered")
    temporary_location: str = Field(
        ...,
        description="product in temporary location when its just arrived",
        min_length=1,
        max_length=100,
    )
    class Config:
        json_schema_extra ={
            "example":{
                "order_id": "Order123",
                "product_id": "Product456",
                "product_name": "Product Name",
                "quantity": 50,
                "temporary_location": "Temporary Location"
            }
        }
    
class QualityCheck(BaseModel):  # Controller Side Report
    product_id: str = Field(
        ..., description="id of product", min_length=1, max_length=100
    )
    quality_check_passed: bool = Field(
        ...,
        description="based on the quality of a product, "
        "it's going to be accepted or rejected",
    )
    spoilage_place: str = Field(
        None,
        description="based on the quality check, the product is moved to the spoilage place",
        min_length=0,
        max_length=100,
    )
    description: str = Field(
        None,
        description="description of a product's state",
        min_length=1,
        max_length=500,
    )
    comment: str = Field(
        None,
        description="based on the value of quality check, if quality check is false",
        max_length=100,
    )
    # hash: str = Field(..., description='a value with which a report can be found in blockchain')
    # pubkey: str = Field(..., description='public key of this report')
    class Config:
        json_schema_extra = {
            "example":{
                "product_id": "Product123",
                "quality_check_passed": True,
                "spoilage_place": "godd",  # No spoilage place as the quality check passed
                "description": "Product in excellent condition",
                "comment": "good job"  # No comment as the quality check passed
            }
        }

class WarehouseAllocation(BaseModel):  # Warehouseman Side Report
    product_id: str = Field(..., description="id of product", max_length=100)
    # hash: str = Field(..., description='a value with which a report can be found in blockchain')
    # pubkey: str = Field(..., description='public key of this report')

    warehouse_row: int = Field(
        ...,
        description="Inside the warehouse are many rows in which product are stored, "
        "they have their own numeration",
        le=100000,
    )
    shelf_num: int = Field(
        ...,
        description="Inside one row are many shelfs,"
        "they differ based on the level inside a row",
        le=100000,
    )
    warehouse_team: list = Field(
        ...,
        description="a team of workers that should receive a product",
    )
    class Config:
        json_schema_extra ={
            "example":{
                "product_id": "Product456",
                "warehouse_row": 42,
                "shelf_num": 3,
                "warehouse_team": ["Worker1", "Worker2", "Worker3"]
            }
        }


class LocationConfirmation(BaseModel):
    product_id: str = Field(
        ..., description="id of product", max_length=100, min_length=1
    )
    location_confirmed: bool = Field(
        ...,
        description="when a product is delivered to its position in warehouse, "
        "workers are going to confirm whether the product has "
        "reached its destination",
    )

    class Config:
        json_schema_extra ={
            "example":{
                "product_id": "Product789",
                "location_confirmed": True
            }
        }


class ProductUnload(BaseModel):
    # product_id: str = Field(
    #     ..., description="id of product", min_length=1, max_length=100
    # )
    quantity : int = Field(...,description="quantity of products")
    temporary_location: str = Field(
        ...,
        description="product in temporary location when its going to be unpacked",
        max_length=100,
    )
    is_unloaded: bool = Field(
        ...,
        description="a field that watches whether a product is unloaded from warehouse location",
    )
    class Config:
        json_schema_extra = {
            "example":{
                "quantity": 10,
                "temporary_location": "Temporary Location",
                "is_unloaded": True
            }

        }


class ProductReturn(BaseModel):
    product_id: str = Field(
        ..., description="id of product", max_length=100, min_length=1
    )
    supplier: str = Field(..., description="Name of the Supplier", max_length=100)
    supplier_address: str = Field(
        ..., description="Address of the Supplier", max_length=100
    )
    sending_date: float = Field(
        ..., description="when a product was sent from supplier"
    )
    package_condition: str = Field(
        ..., description="condition of a package", max_length=100
    )
    quality_complaints: str = Field(
        ..., description="complaints detail", max_length=100
    )
    class Config:
        json_schema_extra ={
            "example":{
                "product_id": "Product123",
                "supplier": "SupplierABC",
                "supplier_address": "123 Supplier St, Supplier City",
                "sending_date": "2023-10-15",
                "package_condition": "Good",
                "quality_complaints": "Product arrived damaged."
            }
        }

# class BookingProduct(BaseModel):
#     # destination: str = Field(
#     #     ..., description="Where product should be delivered", max_length=100
#     # )
#     # booking_date: float = Field(..., description="When product should be delivered")
#     # product_id: str = Field(
#     #     ..., description="Id of product", max_length=100, min_length=1
#     # )
#     # team_of_workers: list = Field(..., description="Responsible team")
#     # temporary_place: str = Field(
#     #     ..., description="A temporary place from where to pick up the goods"
#     # )


# All unduitable models


class InfoProduct(BaseModel):
    product_id: str = Field(None, description="product_id")
    location_id: str = Field(..., description="list_id")

    class Config:
        json_schema_extra ={
            "example":{
                "product_id": "Product123",
                "location_id": "Location456"
            }
        }


class UnsuitablePlace(BaseModel):
    row: int = Field(..., description="row number", ge=1, le=1000000)
    shelf: int = Field(..., description="shelf number", ge=1, le=1000000)
    floor: int = Field(..., description="floor level", ge=1, le=1000000)
    product_id_list: Optional[list] = Field(
        None, description="a team member, who has invoice data"
    )
    # product_info_list: List[InfoProduct] = Field(..., description='product list')
    description: str = Field(..., description="description place", max_length=500)
    priority: str = Field(..., description="major or not", max_length=50)
    creation_date: str = Field(
        default=str(datetime.now().date().isoformat()),
        description="time to create request",
    )

    @field_validator("creation_date")
    @classmethod
    def validate_iso_format_date(cls, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid ISO 8601 format for date")
        return value
    
    class Config:
        json_schema_extra ={
            "example":{
                "row": 10,
                "shelf": 3,
                "floor": 2,
                "product_id_list": ["Product123", "Product456"],
                "description": "Unsafe storage conditions for certain products.",
                "priority": "High",
                "creation_date": "2023-10-20"
            }
        }


class InvoiceUnsuitablePlace(UnsuitablePlace):
    temproary_place: str = Field(
        ..., description="Place to put product)", max_length=100
    )
    responsible_workers: Optional[list] = Field(
        None, description="a team member, who has invoice data"
    )
    creation_date_invoice: str = Field(
        default=str(datetime.now().isoformat()), description="time to create invoice"
    )

    @field_validator("creation_date_invoice")
    @classmethod
    def validate_iso_format(cls, value):
        try:
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            raise ValueError("Invalid ISO 8601 format")
        return value

    class Config:
        json_schema_extra ={
            "example":{
                "row": 15,
                "shelf": 5,
                "floor": 3,
                "product_id_list": ["Product789", "Product101"],
                "description": "Unsuitable storage conditions for certain products.",
                "priority": "High",
                "creation_date": "2023-10-22",
                "temproary_place": "Temporary Storage Area",
                "responsible_workers": ["Worker1", "Worker2"],
                "creation_date_invoice": "2023-10-22T08:30:00.000000"
            }
        }

# Dispatcher web interface model
class DispatcherModel(BaseModel):
    check_document: bool = Field(..., description="check list of document")
    document_description: str = Field(
        None, description="some documents not matched", max_length=500
    )
    check_time: bool = Field(..., description="check_time")
    time_description: str = Field(None, description="order is late", max_length=500)
    list_products: bool = Field(..., description="list products in order")
    products_description: str = Field(
        None, description="product description", max_length=500
    )
    plombs: bool = Field(..., description="plomb of order")
    plombs_description: str = Field(None, description="plombs", max_length=500)
    order_accepted: bool = Field(..., description="order_accepted")
    accepted_description: str = Field(
        None, description="accepted description", max_length=500
    )

    class Config:
        json_schema_extra ={
            "example":{
                "check_document": True,
                "document_description": "Some documents are missing or incomplete. Please review.",
                "check_time": True,
                "time_description": "The order is running late. Notify the client.",
                "list_products": True,
                "products_description": "The product list matches the order requirements.",
                "plombs": True,
                "plombs_description": "The order plombs are intact and in good condition.",
                "order_accepted": True,
                "accepted_description": "The order has been accepted and is ready for dispatch."
            }
        }

# Controller check_packaging model
class PackagingQualityCheck(BaseModel):
    product_name: str = Field(..., description="product name of in order")
    packaging_condition: str = Field(..., description="condition of container")
    packaging_quality: str = Field(..., description="packing condition")
    outer_marking: bool = Field(
        ..., description="the presence of external marking of containers"
    )
    packaging_by: str = Field(..., description="sender of product")
    opening_datetime: datetime = Field(
        default=datetime.now(), description="opening datetime"
    )
    # file: Optional[UploadFile] = None  # Добавление аннотации file

    class Config:
        json_schema_extra ={
            "example":{
                "product_name": "ProductABC",
                "packaging_condition": "Good",
                "packaging_quality": "Excellent",
                "outer_marking": True,
                "packaging_by": "SupplierXYZ",
                "opening_datetime": "2023-10-18T10:30:00.000000"
            }
        }