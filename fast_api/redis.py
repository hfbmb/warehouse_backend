import redis, json
from fastapi import HTTPException
from redis.asyncio import Redis

# Создание подключения к Redis
redis_db = redis.StrictRedis(
    host="app_redis", port=6379, password="Qr_@20", db=0, decode_responses=True
)
async def redis_get(set_data):
    data = redis_db.get(set_data)
    if data is None:
        raise HTTPException(status_code=401, detail="redis key is not found")
    return data


async def redis_verify(token: str) -> str:
    # В функции проверки токена
    data = redis_db.get(token)
    data = json.loads(data)
    if data["token_data"] != token:
        raise HTTPException(status_code=401, detail="Token is invalid")
    else:
        return data["salesman_id"]


async def redis_set(set_data: str, data: dict):
    ttl =900
    # Check if "refresh_token" exists in the data dictionary
    if "refresh_token" in data and data["refresh_token"] == "KeyError":
        pass
    else:
        ttl = 604800
    data = json.dumps(data)
    redis_db.set(set_data, data, ttl)


async def delete(token):
    redis_db.delete(token)
