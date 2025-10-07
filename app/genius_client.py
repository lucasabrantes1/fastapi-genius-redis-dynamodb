import httpx
from .config import settings

class GeniusClient:
    def __init__(self, base_url: str | None = None, token: str | None = None):
        self.base_url = base_url or settings.genius_base_url
        self.token = token or settings.genius_token
        if not self.token:
            raise RuntimeError("GENIUS_TOKEN não configurado")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    async def _get(self, url: str, params: dict | None = None):
        async with httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=20.0
        ) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            return r.json()

    async def search_artist_id(self, artist_name: str) -> int | None:
        """
        Busca o ID do artista no Genius usando /search.
        Tenta casar nome exato (case-insensitive); senão usa o primeiro resultado.
        """
        data = await self._get("/search", params={"q": artist_name})
        hits = data.get("response", {}).get("hits", [])

        lowered = artist_name.lower().strip()
        for h in hits:
            primary = h.get("result", {}).get("primary_artist", {}) or {}
            name = (primary.get("name") or "").lower().strip()
            if name == lowered and primary.get("id"):
                return int(primary["id"])

        for h in hits:
            primary = h.get("result", {}).get("primary_artist", {}) or {}
            if primary.get("id"):
                return int(primary["id"])

        return None

    async def get_top_songs(self, artist_id: int, limit: int = 10) -> list[dict]:
        """
        A API pública não tem 'top songs' oficial; usamos /artists/{id}/songs com sort=popularity,
        paginando levemente e retornando até 'limit' músicas, normalizadas.
        """
        songs: list[dict] = []
        page = 1
        while len(songs) < limit and page <= 3:
            data = await self._get(
                f"/artists/{artist_id}/songs",
                params={"per_page": 20, "page": page, "sort": "popularity"},
            )
            page += 1
            for s in data.get("response", {}).get("songs", []):
                songs.append(s)
                if len(songs) >= limit:
                    break

        norm: list[dict] = []
        for s in songs[:limit]:
            stats = s.get("stats") or {}
            norm.append({
                "id": s.get("id"),
                "title": s.get("title"),
                "url": s.get("url"),
                "full_title": s.get("full_title"),
                "stats_pageviews": stats.get("pageviews"),
            })
        return norm
