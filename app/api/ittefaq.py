"""Ittefaq API routes."""

from typing import List, Optional

import httpx
from fastapi import APIRouter, HTTPException, Query

from app.models.ittefaq import IttefaqNewsItem
from app.services.ittefaq import IttefaqClient

router = APIRouter(prefix="/ittefaq", tags=["Ittefaq"])

ittefaq_client = IttefaqClient()


@router.get(
    "/latest",
    response_model=List[IttefaqNewsItem],
    summary="Fetch latest news from Ittefaq",
)
async def get_latest(
    limit: Optional[int] = Query(
        default=None, ge=1, le=100, description="Number of articles to fetch (1-100)"
    )
):
    """
    Fetch and parse the latest news from Ittefaq portal.

    Args:
        limit: Optional number of articles to fetch. Default is None (fetches all available).

    Returns:
        List of news articles containing:
        - title: Article title
        - link: Full article URL
        - image: Image URL (from CDN)
        - summary: Article summary
        - category: Article category
        - time: Publication time
        - news_body_text_full: Full article body text
    """
    try:
        return await ittefaq_client.fetch_latest(limit=limit)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="Upstream Ittefaq API returned an error.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to reach Ittefaq API.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Unexpected error fetching Ittefaq data."
        ) from exc
