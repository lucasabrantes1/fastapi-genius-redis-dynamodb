import json
from redis import Redis
from .config import settings


class Cache:
    def __init__(self):
        self.client = Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db, decode_responses=True)
        self.ttl = settings.cache_ttl_seconds


    def key_for_artist(self, artist: str) -> str:
        return f"artist:{artist}"


    def get(self, key: str):
        raw = self.client.get(key)
        return json.loads(raw) if raw else None


    def set(self, key: str, value: dict, ttl: int | None = None):
        self.client.setex(key, ttl or self.ttl, json.dumps(value))


    def delete(self, key: str):
        self.client.delete(key)