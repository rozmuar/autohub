"""Review State — Phase 2: отзывы и рейтинги."""

import httpx
import reflex as rx

from app.api import API_V1
from app.state import AppState


class ReviewState(AppState):
    # Write review
    review_order_id: str = ""
    review_rating: int = 0
    review_text: str = ""
    review_loading: bool = False
    review_error: str = ""
    review_done: bool = False

    # Partner reviews page
    reviews_partner_id: str = ""
    reviews: list[dict] = []
    rating_summary: dict = {}
    reviews_loading: bool = False

    # Reply
    reply_review_id: str = ""
    reply_text: str = ""
    reply_loading: bool = False

    async def submit_review(self):
        if self.review_rating == 0:
            self.review_error = "Выберите оценку"
            return
        if not self.review_order_id:
            self.review_error = "Не указан заказ"
            return
        self.review_loading = True
        self.review_error = ""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{API_V1}/reviews",
                    json={
                        "order_id": self.review_order_id,
                        "rating": self.review_rating,
                        "text": self.review_text or None,
                    },
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 201:
                    self.review_done = True
                else:
                    self.review_error = resp.json().get("detail", "Ошибка отправки")
            except Exception:
                self.review_error = "Ошибка соединения"
        self.review_loading = False

    async def load_reviews(self, partner_id: str):
        self.reviews_partner_id = partner_id
        self.reviews_loading = True
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(
                    f"{API_V1}/partners/{partner_id}/reviews",
                    params={"page": 1, "size": 20},
                    timeout=10.0,
                )
                s = await client.get(
                    f"{API_V1}/partners/{partner_id}/rating",
                    timeout=10.0,
                )
                if r.status_code == 200:
                    self.reviews = r.json()
                if s.status_code == 200:
                    self.rating_summary = s.json()
            except Exception:
                pass
        self.reviews_loading = False

    async def submit_reply(self, review_id: str):
        if not self.reply_text or not self.access_token:
            return
        self.reply_loading = True
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.patch(
                    f"{API_V1}/reviews/{review_id}/reply",
                    json={"text": self.reply_text},
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    updated = resp.json()
                    self.reviews = [
                        updated if str(r.get("id")) == review_id else r
                        for r in self.reviews
                    ]
                    self.reply_text = ""
                    self.reply_review_id = ""
            except Exception:
                pass
        self.reply_loading = False

    async def mark_helpful(self, review_id: str):
        if not self.access_token:
            return
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{API_V1}/reviews/{review_id}/helpful",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    count = resp.json().get("helpful_count", 0)
                    self.reviews = [
                        {**r, "helpful_count": count} if str(r.get("id")) == review_id else r
                        for r in self.reviews
                    ]
            except Exception:
                pass

    def set_rating(self, r: int):
        self.review_rating = r
        self.review_error = ""

    def init_review(self, order_id: str):
        self.review_order_id = order_id
        self.review_rating = 0
        self.review_text = ""
        self.review_error = ""
        self.review_done = False

