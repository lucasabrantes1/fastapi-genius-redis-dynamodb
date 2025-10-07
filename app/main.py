from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional


from .schemas import TopTracksResponse, Track
from .genius_client import GeniusClient
from .cache import Cache
from .db import TransactionsRepo
from .utils import norm_artist


app = FastAPI(title="Genius Top Tracks API",
                version="1.0.0",
                description="Lista as 10 músicas mais populares de um artista, com cache em Redis e logging em DynamoDB.")


cache = Cache()
repo = TransactionsRepo()
client = GeniusClient()


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/v1/artists/top-tracks", response_model=TopTracksResponse)
async def top_tracks(
    name: str = Query(..., description="Nome do artista"),
    cache_param: Optional[bool] = Query(None, alias="cache", description="Defina cache=False para forçar atualização"),
):
    artist = norm_artist(name)
    key = cache.key_for_artist(artist)

    force_refresh = (cache_param is False)
    cached = None 

    if not force_refresh:
        cached = cache.get(key)
        if cached:
            resp = TopTracksResponse(
                transaction_id=cached["transaction_id"],
                artist=cached["artist"],
                count=len(cached["tracks"]),
                from_cache=True,
                tracks=[Track(**t) for t in cached["tracks"]],
            )
            return JSONResponse(content=resp.model_dump(), headers={"X-Cache": "HIT"})

    if force_refresh:
        cache.delete(key)

    artist_id = await client.search_artist_id(artist)
    if not artist_id:
        raise HTTPException(status_code=404, detail="Artista não encontrado no Genius")

    tracks_raw = await client.get_top_songs(artist_id, limit=10)
    tracks = [Track(**t).model_dump() for t in tracks_raw]

    transaction_id = repo.put_transaction(
        artist=artist,
        cache_enabled=(cache_param is not False),
        source="genius",
        tracks_count=len(tracks),
    )

    cache.set(key, {"transaction_id": transaction_id, "artist": artist, "tracks": tracks})

    resp = TopTracksResponse(
        transaction_id=transaction_id,
        artist=artist,
        count=len(tracks),
        from_cache=False,
        tracks=[Track(**t) for t in tracks],
    )
    return JSONResponse(
        content=resp.model_dump(),
        headers={"X-Cache": "MISS" if force_refresh else "REBUILT"},
    )
