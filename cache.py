import os
import json
import logging
from typing import Any, Optional
from datetime import datetime
import redis.asyncio as redis
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

class CacheManager:

    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "redis-master.redis.svc.cluster.local")
        self.port = int(os.getenv("REDIS_PORT", 6379))
        self.db = int(os.getenv("REDIS_DB", 0))
        self.password = os.getenv("REDIS_PASSWORD", None)
        self.enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        
        self.redis_client: Optional[redis.Redis] = None
        logger.info(
            f"CacheManager initialized: host={self.host}, port={self.port}, "
            f"db={self.db}, enabled={self.enabled}"
        )

    async def connect(self) -> None:
        if not self.enabled:
            logger.warning("Cache is disabled (CACHE_ENABLED=false)")
            return
            
        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            await self.redis_client.ping()
            logger.info("✓ Connected to Redis")
        except Exception as e:
            logger.error(f"✗ Failed to connect to Redis: {e}")
            self.redis_client = None

    async def disconnect(self) -> None:
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")

    async def get(self, key: str) -> Optional[Any]:
        if not self.enabled or not self.redis_client:
            return None
            
        try:
            value = await self.redis_client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        if not self.enabled or not self.redis_client:
            return False
            
        try:
            serialized = json.dumps(value, default=str)
            await self.redis_client.setex(key, ttl, serialized)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False

    async def exists(self, key: str) -> bool:
        if not self.enabled or not self.redis_client:
            return False
            
        try:
            result = await self.redis_client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache exists error for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        if not self.enabled or not self.redis_client:
            return False
            
        try:
            result = await self.redis_client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False

    async def flush(self) -> bool:
        if not self.enabled or not self.redis_client:
            return False
            
        try:
            await self.redis_client.flushdb()
            logger.info("Cache FLUSHED")
            return True
        except Exception as e:
            logger.error(f"Cache flush error: {e}")
            return False

    async def get_or_set(
        self, key: str, callback, ttl: int = 3600
    ) -> Any:
        cached = await self.get(key)
        if cached is not None:
            return cached
        
        result = await callback()
        
        await self.set(key, result, ttl)
        
        return result


cache_manager = CacheManager()
cache_manager = CacheManager()
cache_manager.set('key', 'value') 