from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, List

import httpx
from bs4 import BeautifulSoup

from app.models.prothom_alo import ProthomAloNewsItem

PROTHOM_ALO_API_BASE = "https://www.prothomalo.com/api/v1/collections/latest-all"
IMAGE_BASE_URL = "https://images.assettype.com/"


class ProthomAloClient:
    """Client wrapper around Prothom Alo's public API."""

    def __init__(self, *, timeout: float = 10.0) -> None:
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    async def fetch_latest(self, limit: int = 10) -> List[ProthomAloNewsItem]:
        """
        Fetch latest news articles from Prothom Alo.

        Args:
            limit: Number of articles to fetch (1-100). Default is 10.

        Returns:
            List of ProthomAloNewsItem objects with full article details.
        """
        # Build URL with limit parameter
        url = f"{PROTHOM_ALO_API_BASE}?item-type=story&offset=0&limit={limit}"

        async with httpx.AsyncClient(
            timeout=self.timeout, headers=self.headers
        ) as client:
            # Fetch latest news from API
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()

            items = self._transform_items(payload)

            # Fetch article bodies for each item
            for item in items:
                item.news_body_text_full = await self._fetch_article_body(
                    client, item.article_url
                )

        return items

    def _transform_items(self, payload: Any) -> List[ProthomAloNewsItem]:
        items = payload.get("items", []) if isinstance(payload, dict) else []
        transformed: List[ProthomAloNewsItem] = []

        for item in items:
            story = item.get("story") if isinstance(item, dict) else None
            if not isinstance(story, dict):
                continue

            hero_key = story.get("hero-image-s3-key") or ""
            sections = story.get("sections") or []
            section_name = (
                sections[0].get("name")
                if sections and isinstance(sections[0], dict)
                else "General"
            )

            transformed.append(
                ProthomAloNewsItem(
                    news_header=story.get("headline") or "",
                    image_url=f"{IMAGE_BASE_URL}{hero_key}" if hero_key else "",
                    publish_time=self._format_publish_time(story.get("published-at")),
                    section=section_name or "General",
                    summary=story.get("summary"),
                    article_url=story.get("url") or "",
                    news_body_text_full="",  # Will be populated later
                )
            )

        return transformed

    @staticmethod
    def _format_publish_time(raw_timestamp: Any) -> str:
        if isinstance(raw_timestamp, (int, float)):
            # Upstream timestamp is in milliseconds
            seconds = float(raw_timestamp) / 1000.0
            return (
                datetime.fromtimestamp(seconds, tz=timezone.utc)
                .isoformat()
                .replace("+00:00", "Z")
            )
        return ""

    async def _fetch_article_body(
        self, client: httpx.AsyncClient, article_url: str
    ) -> str:
        """
        Fetch the full article body from a Prothom Alo article URL.

        Args:
            client: The httpx async client to use for the request.
            article_url: URL of the article to fetch.

        Returns:
            Full article body text, or empty string if fetch fails.
        """
        if not article_url:
            return ""

        try:
            response = await client.get(article_url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract news body text using CSS selector #container p
            body_paragraphs = soup.select("#container p")
            news_body_text_full = "\n\n".join(
                [
                    p.get_text(strip=True)
                    for p in body_paragraphs
                    if p.get_text(strip=True)
                ]
            )

            return news_body_text_full

        except Exception:
            # If fetching article body fails, return empty string
            # This allows the rest of the article data to still be returned
            return ""
