from pydantic import BaseModel,Field

class MigrateDB(BaseModel):
    collection_name : str = Field(...,description="collection name")
    class Config:
        extra = "allow"