"""ContentState — новости, акции, блог."""

import httpx
import reflex as rx
from datetime import datetime

from app.api import API_V1
from app.state import AppState


def _fmt_date(d: str | None) -> str:
    """ISO datetime → ДД.ММ.ГГГГ."""
    if not d:
        return ""
    try:
        dt = datetime.fromisoformat(d.replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y")
    except Exception:
        return d or ""


class Article(rx.Base):
    id: int = 0
    title: str = ""
    slug: str = ""
    excerpt: str = ""
    cover_url: str = ""
    published_at: str = ""
    views_count: int = 0
    content_type: str = ""
    author: str = ""
    promo_discount_pct: int = 0
    promo_valid_until: str = ""


class ContentState(AppState):
    # Список
    articles: list[Article] = []
    total: int = 0
    page: int = 1
    size: int = 12
    pages: int = 1
    content_type: str = "news"
    loading: bool = False

    # Детальная страница
    article: dict = {}
    article_loading: bool = False
    article_error: str = ""
    # Поля детальной страницы
    art_title: str = ""
    art_body: str = ""
    art_cover_url: str = ""
    art_author: str = ""
    art_published_at: str = ""
    art_views_count: int = 0
    art_discount: int = 0
    art_promo_until: str = ""

    # ---------------------------------------------------------------- список

    async def load_news(self):
        self.content_type = "news"
        await self._load_list()

    async def load_promos(self):
        self.content_type = "promo"
        await self._load_list()

    async def load_blog(self):
        self.content_type = "blog"
        await self._load_list()

    async def _load_list(self):
        self.loading = True
        self.articles = []
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(
                    f"{API_V1}/content",
                    params={"type": self.content_type, "page": self.page, "size": self.size},
                    timeout=10.0,
                )
                if r.status_code == 200:
                    data = r.json()
                    raw = data.get("items", [])
                    articles = []
                    for a in raw:
                        articles.append(Article(
                            id=a.get("id", 0),
                            title=a.get("title", ""),
                            slug=a.get("slug", ""),
                            excerpt=a.get("excerpt", "") or a.get("summary", ""),
                            cover_url=a.get("cover_url", "") or a.get("cover_image", ""),
                            published_at=_fmt_date(a.get("published_at")),
                            views_count=a.get("views_count", 0) or 0,
                            content_type=a.get("content_type", "") or a.get("type", ""),
                            author=a.get("author", "") or a.get("author_name", ""),
                            promo_discount_pct=a.get("promo_discount_pct", 0) or 0,
                            promo_valid_until=_fmt_date(a.get("promo_valid_until")),
                        ))
                    self.articles = articles
                    self.total = data.get("total", 0)
                    self.pages = data.get("pages", 1)
            except Exception:
                pass
        self.loading = False

    async def set_page_news(self, p: int):
        self.page = p
        self.content_type = "news"
        await self._load_list()

    async def set_page_promo(self, p: int):
        self.page = p
        self.content_type = "promo"
        await self._load_list()

    async def set_page_blog(self, p: int):
        self.page = p
        self.content_type = "blog"
        await self._load_list()

    # ---------------------------------------------------------------- деталь

    async def load_article_from_url(self):
        slug = self.router.page.params.get("slug", "")
        await self._load_article(slug)

    async def _load_article(self, slug: str):
        if not slug:
            return
        self.article_loading = True
        self.article = {}
        self.article_error = ""
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(f"{API_V1}/content/{slug}", timeout=10.0)
                if r.status_code == 200:
                    a = r.json()
                    self.article = a
                    self.art_title = a.get("title", "")
                    self.art_body = a.get("body", "") or a.get("content", "")
                    self.art_cover_url = a.get("cover_url", "") or a.get("cover_image", "")
                    self.art_author = a.get("author", "") or a.get("author_name", "")
                    self.art_published_at = _fmt_date(a.get("published_at"))
                    self.art_views_count = a.get("views_count", 0) or 0
                    self.art_discount = a.get("promo_discount_pct") or 0
                    self.art_promo_until = _fmt_date(a.get("promo_valid_until")) or ""
                else:
                    self.article_error = "Материал не найден"
            except Exception:
                self.article_error = "Ошибка загрузки"
        self.article_loading = False

