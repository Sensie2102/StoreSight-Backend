import os
import json
import redis.asyncio as redis
from kombu.utils.url import safequote

redis_host = safequote(os.environ.get('REDIS_HOST', 'localhost'))
redis_client = redis.Redis(host=redis_host, port=6379, db=0)

async def add_key_value_redis(key, value, expire=None):
    value = json.dumps(value)
    await redis_client.set(key, value, ex=expire)

async def get_value_redis(key):
    value = await redis_client.get(key)
    return json.loads(value) if value else None

async def delete_key_redis(key):
    await redis_client.delete(key)

async def close_redis():
    await redis_client.close()
    await redis_client.connection_pool.disconnect()
