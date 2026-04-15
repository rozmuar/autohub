"""Search State — partner search and partner detail."""

import httpx
import reflex as rx

from app.api import API_V1
from app.state import AppState


async def _asyncio_gather(*coros):
    import asyncio
    return await asyncio.gather(*coros)


class SearchState(AppState):
    query: str = ""
    category_filter: str = ""
    city_filter: str = ""
    region_filter: str = ""
    sort_by: str = "relevance"
    min_rating: float = 0.0
    lat: float = 0.0
    lon: float = 0.0
    radius_km: int = 10

    results: list[dict] = []
    total: int = 0
    page: int = 1
    loading: bool = False
    error: str = ""

    view_mode: str = "list"
    map_points: list[dict] = []
    map_total: int = 0
    map_loading: bool = False

    selected_partner: dict = {}
    partner_reviews: list[dict] = []
    partner_services: list[dict] = []
    partner_rating: dict = {}
    partner_loading: bool = False

    categories: list[dict] = []

    async def do_search(self):
        self.loading = True
        self.error = ""
        params: dict = {"page": self.page, "size": 20}
        if self.query:
            params["q"] = self.query
        if self.category_filter:
            params["category"] = self.category_filter
        if self.city_filter:
            params["city"] = self.city_filter
        if self.region_filter:
            params["region"] = self.region_filter
        if self.lat and self.lon:
            params["lat"] = self.lat
            params["lon"] = self.lon
            params["radius_km"] = self.radius_km
        if self.sort_by:
            params["sort"] = self.sort_by
        if self.min_rating > 0:
            params["min_rating"] = self.min_rating
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/search/partners",
                    params=params,
                    timeout=15.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, dict):
                        self.results = data.get("items", [])
                        self.total = data.get("total", 0)
                    else:
                        self.results = data
                        self.total = len(data)
                else:
                    self.error = "Ошибка поиска"
            except Exception:
                self.error = "Ошибка соединения с сервером"
        self.loading = False

    async def load_map_points(self):
        self.map_loading = True
        params: dict = {}
        if self.city_filter:
            params["city"] = self.city_filter
        if self.region_filter:
            params["region"] = self.region_filter
        if self.query:
            params["q"] = self.query
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/search/map-points",
                    params=params,
                    timeout=20.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self.map_points = data.get("items", [])
                    self.map_total = len(self.map_points)
            except Exception:
                pass
        self.map_loading = False
        import json
        pts = [
            {
                "id": str(p.get("id", "")),
                "n": p.get("name", ""),
                "lat": p.get("latitude", 0),
                "lon": p.get("longitude", 0),
                "r": p.get("rating", 0),
                "a": p.get("address", "") or "",
                "ph": p.get("phone", "") or "",
            }
            for p in self.map_points
            if p.get("latitude") and p.get("longitude")
        ]
        pts_json = json.dumps(pts)
        yield rx.call_script(
            f"window._ahInitMap && window._ahInitMap(); "
            f"setTimeout(function(){{ window._ahSetPoints && window._ahSetPoints({pts_json}); }}, 500);"
        )

    def set_city_filter(self, city: str):
        self.city_filter = city
        self.page = 1

    def set_region_filter(self, region: str):
        self.region_filter = "" if region == "all" else region
        self.page = 1

    async def load_categories(self):
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(f"{API_V1}/catalog/categories", timeout=10.0)
                if resp.status_code == 200:
                    data = resp.json()
                    self.categories = data.get("items", data) if isinstance(data, dict) else data
            except Exception:
                pass

    async def add_to_favorites(self, partner_id: str):
        if not self.access_token:
            return rx.redirect("/login")
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    f"{API_V1}/users/favorites/{partner_id}",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
            except Exception:
                pass

    def on_query_change(self, q: str):
        self.query = q

    async def on_enter_search(self):
        self.page = 1
        yield SearchState.do_search()

    def set_sort(self, s: str):
        self.sort_by = s

    def set_category(self, c: str):
        self.category_filter = "" if c == "all" else c

    async def switch_to_map(self):
        self.view_mode = "map"
        if not self.map_points:
            yield SearchState.load_map_points()

    async def switch_to_list(self):
        self.view_mode = "list"
        if not self.results:
            yield SearchState.do_search()

    async def load_partner(self, partner_id: str):
        self.partner_loading = True
        self.selected_partner = {}
        self.partner_reviews = []
        self.partner_services = []
        self.partner_rating = {}
        async with httpx.AsyncClient() as client:
            try:
                p_resp, r_resp, s_resp, rat_resp = await _asyncio_gather(
                    client.get(f"{API_V1}/partners/{partner_id}", timeout=10.0),
                    client.get(f"{API_V1}/partners/{partner_id}/reviews",
                               params={"page": 1, "size": 10}, timeout=10.0),
                    client.get(f"{API_V1}/catalog/services",
                               params={"partner_id": partner_id}, timeout=10.0),
                    client.get(f"{API_V1}/partners/{partner_id}/rating", timeout=10.0),
                )
                if p_resp.status_code == 200:
                    self.selected_partner = p_resp.json()
                if r_resp.status_code == 200:
                    self.partner_reviews = r_resp.json()
                if s_resp.status_code == 200:
                    data = s_resp.json()
                    self.partner_services = data.get("items", data) if isinstance(data, dict) else data
                if rat_resp.status_code == 200:
                    self.partner_rating = rat_resp.json()
            except Exception:
                try:
                    p = await client.get(f"{API_V1}/partners/{partner_id}", timeout=10.0)
                    if p.status_code == 200:
                        self.selected_partner = p.json()
                except Exception:
                    pass
        self.partner_loading = False

    async def load_partner_from_url(self):
        partner_id = self.router.page.params.get("partner_id", "").strip('"')
        if partner_id:
            yield SearchState.load_partner(partner_id)