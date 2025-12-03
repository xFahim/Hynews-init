"""Daily Star API routes."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.services.scraper import DailyStarScraper

router = APIRouter(prefix="/dailystar", tags=["Daily Star"])

scraper = DailyStarScraper()


@router.get("/latest")
async def get_latest(
    limit: Optional[int] = Query(
        default=10, ge=1, le=100, description="Number of articles to fetch (1-100)"
    )
):
    """
    Fetch news articles from The Daily Star's Today's News page.

    Args:
        limit: Number of articles to fetch. Default is 10, maximum is 100.

    Returns:
        JSON response with list of articles containing:
        - title: Article title
        - url: Article URL
        - heading: Article heading
        - date_time: Publication date and time
        - image: Main article image URL
        - news_body_text_full: Full article text
    """
    try:
        articles = scraper.fetch_all_articles_with_details(limit=limit)
        return {
            "status": "success",
            "count": len(articles),
            "limit": limit,
            "articles": articles,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch articles: {str(e)}"
        )




