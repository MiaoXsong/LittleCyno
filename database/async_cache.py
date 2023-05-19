import aiocache


class Cache:
    def __init__(self):
        self.cache = aiocache.Cache(aiocache.SimpleMemoryCache)

    async def set(self, key, value, ttl=None):
        """
        将键值对存储到缓存中，可以指定一个可选的过期时间（以秒为单位）。

        如果ttl为None，则键值对将永久存储在缓存中（直到缓存被清除或内存不足）。
        """
        await self.cache.set(key, value, ttl=ttl)

    async def get(self, key):
        """
        从缓存中获取键值对，如果键不存在则返回None。
        """
        return await self.cache.get(key)

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
