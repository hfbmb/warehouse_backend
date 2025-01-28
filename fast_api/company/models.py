# Import necessary packages and modules
from pydantic import BaseModel, Field, EmailStr, field_validator
import re
from typing import Optional

# Define a Pydantic model for an 'Address'
class Address(BaseModel):
    # Define fields for the 'Address' model with validation constraints and descriptions
    zip_code: str = Field(
        ..., description="Zip code of company location", max_length=10
    )
    street: str = Field(
        ..., description="Street of company location", max_length=50
    )
    city: str = Field(
        ..., description="City of company location", max_length=50
    )
    region: str = Field(
        ..., description="Region of company location", max_length=50
    )
    country: str = Field(
        ..., description="Country of company location", max_length=50
    )

    class Config:
        # Provide an example for the 'Address' model in JSON schema format
        json_schema_extra = {
            "example": {
                "zip_code": "zipppp",
                "street": "astana",
                "city": "Astana",
                "region": "Aqmola",
                "country": "Qazaqstan",
            }
        }

# Define a Pydantic model for a 'Company' with various fields and validation constraints
class Company(BaseModel):
    logo: str = Field(..., description="Path of company logo")
    company_name: str = Field(
        ..., description="Company name", min_length=1, max_length=100
    )
    bin_tax_code: str = Field(
        ..., description="BIN Tax-code of company", min_length=1, max_length=20
    )
    website: str = Field(
        ..., description="URL of company website", min_length=1, max_length=100
    )
    office_email: EmailStr = Field(..., description="Email of company")
    # office_password:str = Field(...,description="tested this code")
    telephone_number: int = Field(..., description="Telephone number of company")
    mobile_number: int = Field(..., description="Mobile number of company")
    company_address: Address = Field(..., description="Main address of company")
    stamp: str = Field(..., description="Path of company stamp", max_length=100)

    # Define a validation method for the 'website' field
    @field_validator("website")
    @classmethod
    def validate_website_url(cls, value):
        if not re.match(
            r"(https:\/\/www\.|http:\/\/www\.|https:\/\/|http:\/\/)?[a-zA-Z0-9]{2,}(\.[a-zA-Z0-9]{2,"
            r"})(\.[a-zA-Z0-9]{2,})?",
            value,
        ):
            raise ValueError("Invalid website URL format")
        return value

    class Config:
        # Allow extra fields in the model, and provide an example for the 'Company' model
        extra = "allow"
        json_schema_extra = {
            "example": {
                "logo": "logo.png",
                "company_name": "company1",
                "bin_tax_code": "bin_tax_code",
                "website": "https://chat.openai.com/",
                "office_email": "example@example.com",
                "telephone_number": 988,
                "mobile_number": 123,
                "company_address": {
                    "zip_code": "zipppp",
                    "street": "street",
                    "city": "city1",
                    "region": "region",
                    "country": "country",
                },
                "stamp": "stamp",
            }
        }

# Define a Pydantic model 'ReturnCompany' that inherits from 'Company' and adds an 'id' field
class ReturnCompany(Company):
    id: str = Field(..., description="id of company")
    class Config:
        # Allow extra fields in the model, and provide an example for the 'Company' model
        extra = "allow"
        json_schema_extra = {
            "example": {
                "id":"123231re05",
                "logo": "logo.png",
                "company_name": "company1",
                "bin_tax_code": "bin_tax_code",
                "website": "https://chat.openai.com/",
                "office_email": "example@example.com",
                "telephone_number": 988,
                "mobile_number": 123,
                "company_address": {
                    "zip_code": "zipppp",
                    "street": "street",
                    "city": "city1",
                    "region": "region",
                    "country": "country",
                },
                "stamp": "stamp",
            }
        }

# Define a Pydantic model 'CompanyWithStatus' that inherits from 'Company' and adds a 'status' field
class CompanyWithStatus(Company):
    status: str = Field(..., description="status of the company")
    class Config:
        # Allow extra fields in the model, and provide an example for the 'Company' model
        extra = "allow"
        json_schema_extra = {
            "example": {
                "id":"123231re05",
                "logo": "logo.png",
                "company_name": "company1",
                "bin_tax_code": "bin_tax_code",
                "website": "https://chat.openai.com/",
                "office_email": "example@example.com",
                "telephone_number": 988,
                "mobile_number": 123,
                "company_address": {
                    "zip_code": "zipppp",
                    "street": "street",
                    "city": "city1",
                    "region": "region",
                    "country": "country",
                },
                "stamp": "stamp",
                "status":"company_added"
            }
        }

# Define a Pydantic model 'DeleteWarehouse' for deleting a warehouse with company and warehouse name
class DeleteWarehouse(BaseModel):
    company_name: str = Field(..., description="Company name")
    warehouse_name: str = Field(..., description="Warehouse name")
    class Config:
        json_schema_extra={
            "example":{
                "company_name":"company1",
                "warehouse_name":"warehouse1",
            }
        }

# Define a Pydantic model 'CompanyUpdateInfo' with no specific constraints
class CompanyUpdateInfo(BaseModel):
    class Config:
        extra = "allow"

# Define a Pydantic model 'UpdateCompany' for updating company information with various optional fields
class UpdateCompany(BaseModel):
    logo: str = Field(None, description="Path of company logo")
    company_name: str = Field(None, description="Company name")
    bin_tax_code: str = Field(None, description="BIN Tax-code of company")
    website: str = Field(None, description="URL of company website", scheme=False)
    office_email: EmailStr = Field(None, description="Email of company")
    telephone_number: int = Field(None, description="Telephone number of company")
    mobile_number: int = Field(None, description="Mobile number of company")
    company_address: Optional[Address] = None
    stamp: str = Field(None, description="Path of company stamp")
    
    class Config:
        json_schema_extra={
            "example":{
                "logo": "new_logo.png",
                "company_name": "Updated Company Name",
                "bin_tax_code": "BIN987654321",
                "website": "https://www.updatedcompany.com",
                "office_email": "newinfo@updatedcompany.com",
                "telephone_number": "9876543210",
                # "mobile_number": 1234567890,
                "company_address": {
                    "zip_code": "54321",
                    "street": "Updated Address",
                    "city": "Updated City",
                    "region": "Updated Region",
                    "country": "Updated Country"
                },
                "stamp": "new_stamp.png"
            }
        }

# Define a Pydantic model 'Location' for product location information
class Location(BaseModel):
    product_id: str = Field(
        ..., description="id of a product", min_length=1, max_length=50
    )
    warehouse_row: int = Field(..., description="a rack number of a location", ge=0)
    floor_level: int = Field(
        ..., description="a floor level number of a location", ge=0
    )
    shelf_num: int = Field(..., description="a shelf number of a location", ge=0)

    class Config:
        json_schema_extra ={
            "example":{
                "product_id": "product123",
                "warehouse_row": 2,
                "floor_level": 3,
                "shelf_num": 4
            }
        }
