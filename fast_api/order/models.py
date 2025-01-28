# Installed packages
from pydantic import BaseModel, Field,EmailStr,validator
from datetime import datetime,date
from typing import List

# Local packages
from ..product.models import ClientSideProduct
from ..company.models import Address
from typing import Optional

class RentalData(BaseModel):
    name : str = Field(...,description="warehouse or store")
    address : Optional[Address]=Field(default=None,description="warehouse address")
    property_type:Optional[List[str]]=Field(default=["warehouse"],description="property type")
    total_area :float = Field(default=40,description="total area of warehouse or e.t.c ...")
    indoors_there_is:Optional[List[str]]=Field(default=["internet"])
    description : str =Field(default="very good",description="description of warehouse")
    price:float = Field(default=10,description="warehouse price",ge=10)
    phone_number : str = Field(default="8-705-555-10-11",description="phone number of user")
    class Config:
        json_schema_extra = {
            "example":{
                "name":"QR",
                "address":{
                    "zip_code": "zipppp",
                    "street": "street",
                    "city": "city",
                    "region": "region",
                    "country": "country",
                },
                "property_type":["warehouse","store"],
                "total_area":50,
                "indoors_there_is":["internet"],
                "description":"very good",
                "price":100,
                "phone_number":"+7707-870-65-78",
            }
        }

class Order(BaseModel):
    products: List[ClientSideProduct] = Field(..., description="A list of products")
    company_name: str = Field(..., description="Sender company name", max_length=100)
    bin_tax_code: str = Field(..., description="Tax code", max_length=20)
    first_name: str = Field(..., description="Name of the client", max_length=50)
    # last_name:str = Field(...,description="Name of the client")
    second_name: str = Field(
        ..., description="Second name of the client", max_length=50
    )
    e_mail: EmailStr = Field(..., description="email of the client", max_length=100)
    telephone: str = Field(..., description="tel num", max_length=20)
    user_address : Address = Field(...,description="client address")
    date: str = Field(
        default=str(datetime.now().date().isoformat()),
        description="date when an order was created",
    )
    time: str = Field(
        default=str(datetime.now().time().isoformat()),
        description="time when an order was created",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "sender1",
                "bin_tax_code": "sender1",
                "first_name": "client1",
                "second_name": "client1",
                "e_mail": "email@gmail.com",
                "telephone": "tel",
                "user_address":{
                    "zip_code": "zipppp",
                    "street": "street",
                    "city": "city",
                    "region": "region",
                    "country": "country",
                },
                "date": "2023-07-26",
                "time": "09:27",
                "products": [
                    {
                        "product_name": "product_name",
                        "serial_number": "xerftgyhujik",
                        "quantity": 1,
                        "price": 0.0,
                        # "product_category": "milky",
                        "weight": 1.1,
                        "height": 1,
                        "width": 1,
                        "length": 1,
                        "packing_type": "pallets",
                        "dimension_type": "container",
                        "weight_type": "container",
                        "expiration_date": 1.1,
                    }
                ],
                "documents": ["contract.pdf", "invoice.pdf"],
            }
        }


class OrderWithId(Order):
    id: str = Field(..., description="Id of order")
    status: str = Field(..., description="status of order")
    recipient: str = Field(..., description="the company name of recipient")

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "sender1",
                "bin_tax_code": "sender1",
                "first_name": "client1",
                "second_name": "client1",
                "e_mail": "email@gmail.com",
                "telephone": "tel",
                "date": "2023-07-26",
                "time": "09:27",
                "products": [
                    {
                        "product_name": "product_name",
                        "serial_number": "xerftgyhujik",
                        "quantity": 1,
                        "price": 0.0,
                        # "product_category": "milky",
                        "weight": 1.1,
                        "height": 1,
                        "width": 1,
                        "length": 1,
                        "packing_type": "pallets",
                        "dimension_type": "cm",
                        "weight_type": "kg",
                    }
                ],
                "documents": ["contract.pdf", "invoice.pdf"],
                "status": "Order added",
                "recipient": "company1",
                "id": "4def5r6gt7hy5r6t7y",
            }
        }


class SalesmanSideOrder(BaseModel):
    document_number: str = Field(None, description="Document number", max_length=50)
    document_type: str = Field(None, description="Document type", max_length=50)
    description: str = Field(None, description="Description salesman", max_length=250)
    # documents: List[str] = Field(..., description="A list of documents: contract, invoice, etc.")
    warehouse_name: str = Field(..., description="Warehouse name", max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "document_number": "1234er1",
                "document_type": "Nakladnoy",
                "description":"order added",
                # "warehouse_name":"warehouse1"
                }
        }

class SalesmanBox(BaseModel):
    box_id:str =Field(...,description="box id in warehouse")
    box_type_id:str =Field(...,description="box type id")
    products : list =Field(default=None,description="list of product")
    status:str = Field(default="in_waiting",description="box status")

    class Config:
        json_schema_extra={
            "example":{
                "box_id":"123asd",
                "box_type_id":"12qew",
                "products":[
                    {
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
                        "expiration_date": 1.1
                    }
                ],
                "status":"in_waiting"
            }
        }

class SalesmanProductTobox(BaseModel):
    # order_id:str =Field(...,description="order id")
    boxes : Optional[list[SalesmanBox]]= Field(default=None,description="box detail")

    

class CellWithId(BaseModel):
    cell_id:str = Field(...,description="cell_id of cell")
    time_duration : int = Field(default=1,description="time duration of time")

class RentCellByClient(CellWithId):
    cells_with_id:Optional[list[CellWithId]] = Field(default=None)



###This class for create sub order
class Suborder(BaseModel):
    warehouse_name: str = Field(..., description="warehouse name",max_length=50)
    products: list[ClientSideProduct] = Field(..., description="list of product data")
    date_to_arrival: int = Field(..., description="date to arrival order")
    time_to_arrival: int = Field(..., description="time to arrival order")
    status:str =Field(default="created",description="status of sub_order")

    @validator("date_to_arrival", pre=True, always=True)
    def validate_date(cls, value):
        arrival_date = datetime.fromtimestamp(value).date()
        current_date = date.today()
        if arrival_date < current_date:
            raise ValueError("The date must be a future date")
        return value

    @validator("time_to_arrival", pre=True, always=True)
    def validate_time(cls, value, values):
        arrival_time = datetime.fromtimestamp(value).time()
        current_time = datetime.now().time()
        arrival_date = values.get('date_to_arrival')
        if arrival_date:
            arrival_date = datetime.fromtimestamp(arrival_date).date()
            current_date = date.today()
            if arrival_date < current_date and arrival_time <= current_time:
                raise ValueError("The time must be a future time for today's date")
        return value
    
    class Config:
        json_schema_extra={
            "example":{
                "warehouse_name":"warehouse1",
                "products":[
                    {
                        "product_name":"apple",
                        "quantity":10,
                        "expiration_date":10,
                    }
                ],
                # "date_to_storage":10,
                "date_to_arrival":1701129600,
                "time_to_arrival":1701129600,
                "status":"created"
            }
        }


class SubOrders(BaseModel):
    order_id:str =Field(...,description="main order id",min_length=2)
    sub_orders : list[Suborder]=Field(...,description="list of suborder")

    class Config:
        json_schema_extra ={
            "example":{
                "order_id":"12323weqwe",
                "sub_orders":[
                    {
                        "warehouse_name":"warehouse1",
                        "products":[
                            {
                                "product_name":"apple",
                                "quantity":10,
                                "expiration_date":10,
                            }
                        ],
                        # "date_to_storage":10,
                        "date_to_arrival":1701129600,
                        "time_to_arrival":1701129600,
                        "status":"created"
                    },
                    {
                        "warehouse_name":"warehouse2",
                        "products":[
                            {
                                "product_name":"apple",
                                "quantity":10,
                                "expiration_date":10,
        
                            }
                        ],
                        # "date_to_storage":10,
                        "date_to_arrival":1701129600,
                        "time_to_arrival":1701129600,
                        "status":"created"
                    }
                ]
            }
        }