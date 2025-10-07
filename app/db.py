import boto3
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from .config import settings


class TransactionsRepo:
    def __init__(self):
        kwargs = {"region_name": settings.aws_region}
        
        if settings.aws_endpoint_url_dynamodb:
            kwargs["endpoint_url"] = settings.aws_endpoint_url_dynamodb
            
        self.ddb = boto3.resource("dynamodb", **kwargs)
        self.table = self.ddb.Table(settings.ddb_table)

    def now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def expires_epoch(self, days: int = 7) -> int:
        return int((datetime.now(timezone.utc) + timedelta(days=days)).timestamp())

    def put_transaction(self, artist: str, cache_enabled: bool, source: str, tracks_count: int, transaction_id: str | None = None) -> str:
        tid = transaction_id or str(uuid4())
        
        item = {
            "transaction_id": tid,
            "artist_name": artist,
            "cache_enabled": cache_enabled,
            "source": source,
            "tracks_count": tracks_count,
            "created_at": self.now_iso(),
            "ttl": self.expires_epoch(8)
        }
        
        self.table.put_item(Item=item)
        return tid