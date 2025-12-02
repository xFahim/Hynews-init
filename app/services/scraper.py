"""News scraper service for The Daily Star."""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin
from app.services.image_extractor import ImageExtractor


class DailyStarScraper:
    """Scraper for The Daily Star news website."""

    BASE_URL = "https://www.thedailystar.net"
    TODAYS_NEWS_URL = f"{BASE_URL}/todays-news"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    def fetch_news_headings(self) -> List[Dict[str, str]]:
        """
        Fetch news headings from The Daily Star's Today's News page.

        Returns:
            List of dictionaries containing 'title' and 'url' for each news item.
        """
        try:
            response = self.session.get(self.TODAYS_NEWS_URL, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Find all links matching the CSS selector
            news_links = soup.select(".title a")

            news_items = []
            seen_urls = set()  # To avoid duplicates

            for link in news_links:
                href = link.get("href", "")
                # Ensure href is a string
                if isinstance(href, list):
                    href = href[0] if href else ""
                href = str(href) if href else ""

                title = link.get_text(strip=True)

                # Skip empty titles or URLs
                if not title or not href:
                    continue

                # Make URL absolute if it's relative
                full_url = urljoin(self.BASE_URL, href)

                # Avoid duplicates
                if full_url not in seen_urls:
                    seen_urls.add(full_url)
                    news_items.append({"title": title, "url": full_url})

            return news_items

        except requests.RequestException as e:
            raise Exception(f"Failed to fetch news: {str(e)}")
        except Exception as e:
            raise Exception(f"Error parsing news: {str(e)}")

    def fetch_article_details(self, article_url: str) -> Dict[str, str]:
        """
        Fetch full article details from a specific article URL.

        Args:
            article_url: URL of the article to fetch.

        Returns:
            Dictionary containing heading, date_time, image, and news_body_text_full.
        """
        try:
            response = self.session.get(article_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract heading
            heading_elem = soup.select_one(".article-title")
            heading = heading_elem.get_text(strip=True) if heading_elem else ""

            # Extract date-time
            date_time_elem = soup.select_one(".color-iron")
            date_time = date_time_elem.get_text(strip=True) if date_time_elem else ""

            # Extract image URL
            image_url = ImageExtractor.extract_image_url(soup)

            # Extract news body text (all paragraphs)
            body_paragraphs = soup.select(".clearfix p")
            news_body_text_full = "\n\n".join(
                [
                    p.get_text(strip=True)
                    for p in body_paragraphs
                    if p.get_text(strip=True)
                ]
            )

            return {
                "heading": heading,
                "date_time": date_time,
                "image": image_url,
                "news_body_text_full": news_body_text_full,
            }

        except requests.RequestException as e:
            raise Exception(f"Failed to fetch article: {str(e)}")
        except Exception as e:
            raise Exception(f"Error parsing article: {str(e)}")

    def fetch_all_articles_with_details(
        self, limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Fetch news headings and their full article details.

        Args:
            limit: Optional limit on number of articles to fetch. If None, fetches all.

        Returns:
            List of dictionaries containing all article information.
        """
        try:
            # First, get all news headings
            news_items = self.fetch_news_headings()

            # Apply limit if specified
            if limit:
                news_items = news_items[:limit]

            # Fetch details for each article
            articles_with_details = []
            for item in news_items:
                try:
                    article_details = self.fetch_article_details(item["url"])
                    articles_with_details.append(
                        {
                            "title": item["title"],
                            "url": item["url"],
                            **article_details,
                        }
                    )
                except Exception as e:
                    # If fetching details fails for one article, continue with others
                    articles_with_details.append(
                        {
                            "title": item["title"],
                            "url": item["url"],
                            "heading": "",
                            "date_time": "",
                            "image": "",
                            "news_body_text_full": f"Error fetching article: {str(e)}",
                        }
                    )

            return articles_with_details

        except Exception as e:
            raise Exception(f"Failed to fetch articles with details: {str(e)}")
