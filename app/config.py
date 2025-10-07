from pydantic import BaseModel
from dotenv import load_dotenv
import os


load_dotenv()


class Settings(BaseModel):
    genius_token: str = os.getenv("GENIUS_TOKEN", "")
    genius_base_url: str = os.getenv("GENIUS_BASE_URL", "https://api.genius.com")


    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", 6379))
    redis_db: int = int(os.getenv("REDIS_DB", 0))
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", 604800)) # 7 dias


    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    ddb_table: str = os.getenv("DDB_TABLE", "artist_transactions")
    aws_endpoint_url_dynamodb: str | None = os.getenv("AWS_ENDPOINT_URL_DYNAMODB") or None


settings = Settings()