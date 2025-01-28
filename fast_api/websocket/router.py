# Installed packages
from fastapi import WebSocket, APIRouter,Depends
from datetime import datetime
from ..dependencies import get_current_user,check_role_access
from ..user.models import DBUser
from .script import migrate_data_to_include_fields_with_defaults
from .model import MigrateDB

# from jose import JWTError
# from ..utils import decode_access_token
# from ..constants import Errors
# from ..user.service import get_user_by
# import json

# Local packages
from .manager import ConnectionManager
# from ..dependencies import get_current_user

# ...

router = APIRouter(prefix="/websocket", tags=["websocket"])

manager = ConnectionManager()  # Create an instance of ConnectionManager

@router.get('/', response_model=dict)
async def home():
    return await manager.get_active_connections()  # Call the method on the instance
@router.post('/migrate/{collection_name}',response_model=dict )
async def migrate_db(collection_name:str,
                     m_data:MigrateDB,
                     current_user:DBUser=Depends(get_current_user)):
    check_role_access(current_user.role,["admin"])
    m_data = m_data.dict()
    await migrate_data_to_include_fields_with_defaults(collection_name,m_data)
    return {"success":"successfully migrated this data"}

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id:str):
    await manager.connect(user_id, websocket)
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    try:
        while True:
            data = await websocket.receive_text()
            message = {"time":current_time,"client_id":user_id,"message":data}
            await manager.send_message_to_all(message=str(message))

    except Exception as e:
        print("****",e)
        manager.disconnect(user_id, websocket)



# async def get_user(access_token:str):
#     try:
#         if access_token is None:
#             raise HTTPException(status_code=403,detail=Errors.invalid_token)
#         payload = decode_access_token(access_token)
#         if not payload:
#             raise HTTPException(status_code=403, detail=Errors.invalid_token)
#         username: str = payload.get("sub")
#         if username is None:
#             raise HTTPException(status_code=401, detail=Errors.cntv_credentials)
#     except JWTError:
#         raise HTTPException(status_code=401, detail=Errors.cntv_credentials)
#     user = await get_user_by("email", username)
#     return user