from pydantic import BaseModel,Field,EmailStr,validator
from typing import List
from datetime import datetime,timedelta
from ..company.models import Address
import time

class ProductData(BaseModel):
    product_name : str = Field(...,description="product_name")
    warehouse : str = Field(...,description="warehouse name")
    sku: str = Field(..., description="sku of product", min_length=1, max_length=25)
    quantity: int = Field(..., description="quantity of product", ge=1)
    
    class Config:
        json_schema_extra ={
            "example":{
                "product_name": "apple",
                "warehouse": "warehouse1",
                "sku": "SKU12345",
                "quantity": 10
            }
        }

class ShipmentOrder(BaseModel):
    company_name : str = Field(...,description="company name")
    products: List[ProductData] = Field(
        None, description="List of products", min_items=1, max_items=20
    )
    recipients_name: str = Field(
        None,
        description="The name of the recipient of the goods",
        min_length=1,
        max_length=100,
    )
    shipped_date: datetime = Field(
        default=datetime.now(),
        description="Date of shipment (format: yyyy-mm-dd-hh-mm)",
        example="2023-09-30-14-30",  # Замените примером на нужное вам значение
    )

    delivery_address: str = Field(
        ...,
        description="Address where the goods will be delivered",
        min_length=1,
        max_length=100,
    )
    delivery_service: str = Field(
        ..., description="Delivery service for shipping", min_length=1, max_length=50
    )
    # shipment_status : str = Field(default='created')
    additional_comments: str = Field(
        None, description="Additional comments", max_length=150
    )
    @validator("shipped_date")
    def validate_shipped_date(cls, value):
     # Проверяем, что дата не попадает на выходные (суббота или воскресенье)
        if value.weekday() >= 5:
            raise ValueError("The date can't be on a weekend")
        # Устанавливаем рабочее время с 8:00 до 19:00
        work_start = datetime(value.year, value.month, value.day, 8, 0)
        work_end = datetime(value.year, value.month, value.day, 19, 0)
        # Проверяем, что дата и время находятся в рабочем интервале
        if value < work_start or value > work_end:
            raise ValueError("Date and time must be during business hours (8:00 to 19:00)")
        # Проверяем, что дата больше текущей даты плюс один день
        min_date = datetime.now() + timedelta(hours=3)
        if value < min_date:
            raise ValueError("The date must be no earlier than 3 hours")

        return value
    
    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "company_name": "company1",
                # "first_name": "Qazaq",
                # "last_name": "Eli",
                # "telephone_number": "8-705-555-12-34",
                # "warehouse": "warehouse1",
                "products": [
                  {
                    "product_name": "Banan",
                    "sku": "123",
                    "warehouse":"warehouse1",
                    "quantity": 2
                  }
                ],
                # "user_address":{
                #     "zip_code":"123",
                #     "street":"street",
                #     "city":"astana",
                #     "region":"astana",
                #     "country":"Qazaqstan"
                # },
                "recipients_name": "sender",
                "shipped_date": "2023-09-27T09:22:19.160048",
                "delivery_address": "heloo",
                "delivery_service": "car",
                "additional_comments": "hello"
            }
        }

class ShipmentOrderWithID(ShipmentOrder):
    id : str = Field(...,description="shipment order id")

class Update_Shipment_order(BaseModel):
    company_name : str = Field(None,description="company name")
    first_name : str = Field(None,description="first_name of client")
    last_name :str = Field(None,description="last name of client")
    telephone_number : str = Field(None,description="number of telephone")
    warehouse: str = Field(
        ..., description="warehouse info", min_length=1, max_length=100
    )
    products: List[ProductData] = Field(
        ..., description="List of products", min_items=1, max_items=20
    )
    client_email : EmailStr = Field(None, description="email of the user")
    recipients_name: str = Field(
        ...,
        description="The name of the recipient of the goods",
        min_length=1,
        max_length=100,
    )
    shipped_date: str = Field(
        default=datetime.now().isoformat(), description="Date of shipment"
    )
    delivery_address: str = Field(
        ...,
        description="Address where the goods will be delivered",
        min_length=1,
        max_length=100,
    )
    delivery_service: str = Field(
        ..., description="Delivery service for shipping", min_length=1, max_length=50
    )
    # shipment_status : str = Field(default='created')
    additional_comments: str = Field(
        None, description="Additional comments", max_length=150
    )
    @validator("shipped_date")
    def validate_shipped_date(cls, value):
         # Проверяем, что дата не попадает на выходные (суббота или воскресенье)
        if value.weekday() >= 5:
            raise ValueError("The date can't be on a weekend")
        # Устанавливаем рабочее время с 8:00 до 19:00
        work_start = datetime(value.year, value.month, value.day, 8, 0)
        work_end = datetime(value.year, value.month, value.day, 19, 0)
        # Проверяем, что дата и время находятся в рабочем интервале
        if value < work_start or value > work_end:
            raise ValueError("Date and time must be during business hours (8:00 to 19:00)")
        # Проверяем, что дата больше текущей даты плюс один день
        min_date = datetime.now() + timedelta(hours=3)
        if value < min_date:
            raise ValueError("The date must be no earlier than 3 hours")

        return value

    class Config:
        json_schema_extra ={
            "example":{
                "company_name": "CompanyXYZ",
                "first_name": "John",
                "last_name": "Doe",
                "telephone_number": "123-456-7890",
                "warehouse": "Warehouse123",
                "products": [
                    {
                        "product_name": "ProductA",
                        "warehouse": "Warehouse123",
                        "sku": "SKU12345",
                        "quantity": 50
                    },
                    {
                        "product_name": "ProductB",
                        "warehouse": "Warehouse123",
                        "sku": "SKU67890",
                        "quantity": 30
                    }
                ],
                "client_email": "john.doe@example.com",
                "recipients_name": "Jane Smith",
                "shipped_date": "2023-10-18T14:30:00.000000",
                "delivery_address": "123 Main St, Cityville",
                "delivery_service": "Express Shipping",
                "additional_comments": "Handle with care and mark as fragile."
            }
        }

# class UpdateOrderDate(BaseModel):
#     new_date: datetime = Field(
#         default=datetime.now() + timedelta(days=1),
#         description="shipped date"
#     )
#     description: str = Field(None, description="order details")

#     @validator("new_date")
#     def validate_new_date(cls, value):
#         # Проверяем, что дата не попадает на выходные (суббота или воскресенье)
#         if value.weekday() >= 5:
#             raise ValueError("The date can't be on a weekend")
#         # Устанавливаем рабочее время с 8:00 до 19:00
#         work_start = datetime(value.year, value.month, value.day, 8, 0)
#         work_end = datetime(value.year, value.month, value.day, 19, 0)
#         # Проверяем, что дата и время находятся в рабочем интервале
#         if value < work_start or value > work_end:
#             raise ValueError("Date and time must be during business hours (8:00 to 19:00)")
#         # Проверяем, что дата больше текущей даты плюс один день
#         min_date = datetime.now() + timedelta(hours=3)
#         if value < min_date:
#             raise ValueError("The date must be no earlier than 3 hours")

#         return value

