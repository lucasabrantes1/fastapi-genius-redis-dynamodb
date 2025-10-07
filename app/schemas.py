from pydantic import BaseModel, Field
from typing import List, Optional


class Track(BaseModel):
    id: int
    title: str
    url: str
    full_title: str
    stats_pageviews: Optional[int] = None


class TopTracksResponse(BaseModel):
    transaction_id: str = Field(..., description="UUID v4 da transação registrada")
    artist: str
    count: int
    from_cache: bool
    tracks: List[Track]