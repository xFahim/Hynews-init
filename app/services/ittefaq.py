"""Ittefaq news service."""

import json
from typing import List, Optional

import httpx
from bs4 import BeautifulSoup

from app.models.ittefaq import IttefaqNewsItem

ITTEFAQ_API_BASE_URL = "https://www.ittefaq.com.bd/api/theme_engine/get_ajax_contents"
IMAGE_CDN_BASE = "https://cdn.ittefaqbd.com/contents/cache/images"


class IttefaqClient:
    """Client for fetching news from Ittefaq portal."""

    def __init__(
        self,
        *,
        timeout: float = 10.0,
        default_count: int = 20,
        image_dimensions: str = "1100x618x1",
    ) -> None:
        """
        Initialize Ittefaq client.

        Args:
            timeout: Request timeout in seconds. Default is 10.0.
            default_count: Default number of articles to fetch from API. Default is 20.
            image_dimensions: Image dimensions for CDN URLs (format: WIDTHxHEIGHTxQUALITY). Default is "1100x618x1".
        """
        self.timeout = timeout
        self.default_count = default_count
        self.image_dimensions = image_dimensions
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    async def fetch_latest(
        self, limit: Optional[int] = None, count: Optional[int] = None
    ) -> List[IttefaqNewsItem]:
        """
        Fetch latest news articles from Ittefaq.

        Args:
            limit: Optional limit on number of articles to return. If None, returns all fetched articles.
            count: Optional number of articles to fetch from API. If None, uses default_count.

        Returns:
            List of IttefaqNewsItem objects with parsed news data.
        """
        # Use provided count or fall back to default
        api_count = count if count is not None else self.default_count

        # Build API URL with count parameter
        api_url = (
            f"{ITTEFAQ_API_BASE_URL}?widget=476&start=0&count={api_count}"
            f"&page_id=0&subpage_id=0&author=0&tags=&archive_time=&filter="
        )

        async with httpx.AsyncClient(
            timeout=self.timeout, headers=self.headers
        ) as client:
            # Fetch news from API
            response = await client.get(api_url)
            response.raise_for_status()
            payload = response.json()

            # Extract HTML from the response
            html_content = payload.get("html", "")
            if not html_content:
                return []

            # Parse HTML and extract news items
            items = self._parse_html(html_content)

            # Apply limit if specified
            if limit:
                items = items[:limit]

            # Fetch full article body for each item
            for item in items:
                item.news_body_text_full = await self._fetch_article_body(
                    client, item.link
                )

            return items

    def _parse_html(self, html_content: str) -> List[IttefaqNewsItem]:
        """
        Parse HTML content and extract news items.

        Args:
            html_content: Raw HTML string from the API response.

        Returns:
            List of IttefaqNewsItem objects.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        news_items = []

        # Find all news items (divs with class 'each')
        news_divs = soup.find_all("div", class_="each")

        for div in news_divs:
            try:
                # Extract title and link
                title_elem = div.select_one("h2.title > a")
                title = title_elem.get_text(strip=True) if title_elem else ""
                link_raw = title_elem.get("href", "") if title_elem else ""
                link = str(link_raw) if link_raw else ""

                # Prepend https: if link starts with //
                if link.startswith("//"):
                    link = f"https:{link}"

                # Extract summary
                summary_elem = div.select_one("div.summery")
                summary = summary_elem.get_text(strip=True) if summary_elem else ""

                # Extract category
                category_elem = div.select_one("a.category")
                category = category_elem.get_text(strip=True) if category_elem else ""

                # Extract time (try data-published attribute first, then span.time)
                time = ""
                time_elem = div.select_one("span.time")
                if time_elem:
                    time_raw = time_elem.get(
                        "data-published", ""
                    ) or time_elem.get_text(strip=True)
                    time = str(time_raw) if time_raw else ""

                # Extract image from data-ari attribute
                image = self._extract_image(div)

                # Only add item if it has at least a title
                if title:
                    news_items.append(
                        IttefaqNewsItem(
                            title=title,
                            link=link,
                            image=image,
                            summary=summary,
                            category=category,
                            time=time,
                            news_body_text_full="",  # Will be populated later
                        )
                    )

            except Exception:
                # If parsing one item fails, continue with others
                continue

        return news_items

    def _extract_image(self, div) -> str:
        """
        Extract image URL from a news item div.

        The image is stored in a <span> tag with a data-ari attribute
        containing a JSON string with a 'path' field.

        Args:
            div: BeautifulSoup element representing a news item.

        Returns:
            Full image URL, or empty string if extraction fails.
        """
        try:
            # Find span with data-ari attribute
            span_elem = div.find("span", attrs={"data-ari": True})
            if not span_elem:
                return ""

            # Get the data-ari attribute value (JSON string)
            data_ari = span_elem.get("data-ari", "")
            if not data_ari:
                return ""

            # Parse the JSON string
            ari_data = json.loads(data_ari)
            path = ari_data.get("path", "")
            if path:
                # Clean path: remove leading slash to avoid double slashes
                path = path.lstrip("/")
                # Construct full image URL with CDN base URL and dimensions
                return f"{IMAGE_CDN_BASE}/{self.image_dimensions}/uploads/{path}"

        except (json.JSONDecodeError, AttributeError, Exception):
            # If JSON parsing or extraction fails, return empty string
            return ""

        return ""

    async def _fetch_article_body(
        self, client: httpx.AsyncClient, article_url: str
    ) -> str:
        """
        Fetch the full article body from an Ittefaq article URL.

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

            # Extract news body text using CSS selector .jw_article_body
            body_elem = soup.select_one(".jw_article_body")
            if body_elem:
                # Get all paragraphs within the article body
                paragraphs = body_elem.find_all("p")
                news_body_text_full = "\n\n".join(
                    [
                        p.get_text(strip=True)
                        for p in paragraphs
                        if p.get_text(strip=True)
                    ]
                )
                return news_body_text_full

            return ""

        except Exception:
            # If fetching article body fails, return empty string
            # This allows the rest of the article data to still be returned
            return ""
