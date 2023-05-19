import time

import aiocache


class Cache:
    def __init__(self):
        self.cache = aiocache.Cache(aiocache.Cache.MEMORY)

    async def set(self, key, value):
        """
        将键值对存储到缓存中，可以指定一个可选的过期时间（以秒为单位）。

        如果ttl为None，则键值对将永久存储在缓存中（直到缓存被清除或内存不足）。
        """
        # 存储值和当前的时间戳
        await self.cache.set(key, (time.time(), value))

    async def get(self, key, ttl=None):
        """
        从缓存中获取键值对，如果键不存在则返回None。

        如果键存在，但其对应的值已经过期，则返回None。
        """
        result = await self.cache.get(key)
        if result is not None:
            timestamp, value = result
            if ttl is not None and time.time() - timestamp > ttl:
                # 如果值已经过期，返回None，并从缓存中删除该键
                await self.cache.delete(key)
                return None
            else:
                return value
        else:
            return None

    async def delete(self, key):
        """
        从缓存中删除给定的键。如果键不存在，则此操作无效果。
        """
        await self.cache.delete(key)

    async def clear(self):
        """
        清除缓存中的所有键值对。
        """
        await self.cache.clear()
