"""Prothom Alo API routes."""

import httpx
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.models.prothom_alo import ProthomAloNewsItem
from app.services.prothom_alo import ProthomAloClient

router = APIRouter(prefix="/prothomalo", tags=["Prothom Alo"])

prothom_alo_client = ProthomAloClient()


@router.get(
    "/latest",
    response_model=List[ProthomAloNewsItem],
    summary="Fetch latest stories from Prothom Alo",
)
async def get_latest(
    limit: Optional[int] = Query(
        default=10, ge=1, le=100, description="Number of articles to fetch (1-100)"
    )
):
    """
    Fetch and normalize the latest stories from Prothom Alo.

    Args:
        limit: Number of articles to fetch. Default is 10, maximum is 100.

    Returns:
        List of news articles containing:
        - news_header: Article headline
        - image_url: Hero image URL
        - publish_time: Publication timestamp (ISO format)
        - section: Article section/category
        - summary: Article summary (can be null)
        - article_url: Full article URL
        - news_body_text_full: Full article body text
    """
    try:
        return await prothom_alo_client.fetch_latest(limit=limit)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="Upstream Prothom Alo API returned an error.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to reach Prothom Alo API.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Unexpected error fetching Prothom Alo data."
        ) from exc


