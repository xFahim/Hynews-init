"""AI Summary API routes."""

from fastapi import APIRouter, HTTPException, Path, Query
from typing import Dict, Any
import logging

from app.services.scraper import DailyStarScraper
from app.services.prothom_alo import ProthomAloClient
from app.services.ittefaq import IttefaqClient
from app.services.ai_summary import get_ai_summary_service
from app.services.cache_service import get_cache_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summary", tags=["AI Summary"])

# Initialize scrapers/clients
daily_star_scraper = DailyStarScraper()
prothom_alo_client = ProthomAloClient()
ittefaq_client = IttefaqClient()


@router.get("/{source}")
async def get_daily_summary(
    source: str = Path(
        ...,
        description="News source: 'daily-star', 'prothom-alo', or 'ittefaq'"
    ),
    cache: str = Query(
        "on",
        description="Cache control: 'on' (default) to use cache, 'off' to fetch fresh data"
    )
) -> Dict[str, Any]:
    """
    Generate an AI-powered daily executive briefing for a specific news source.

    This endpoint:
    1. Checks cache for existing summary (if cache=on)
    2. Fetches the latest 20 news articles from the specified source
    3. Uses the top 15 articles to generate an AI summary
    4. Returns a structured briefing with categories and "Story of the Day"
    5. Saves result to cache for future requests (if cache=on)

    Args:
        source: The news source to summarize. Options:
            - 'daily-star': The Daily Star
            - 'prothom-alo': Prothom Alo
            - 'ittefaq': Ittefaq
        cache: Cache control parameter. Options:
            - 'on' (default): Use cached summaries and save new ones
            - 'off': Bypass cache and generate fresh summary

    Returns:
        JSON object containing:
        - story_of_day: Object with title and summary of most significant story
        - categories: List of categorized news takeaways
        - metadata: Source information and article count

    Raises:
        HTTPException: 
            - 503 if news fetching fails
            - 500 if AI generation fails
            - 400 if invalid source is provided
    """
    # Normalize source name
    source_lower = source.lower()

    # Check cache first (only if cache is enabled)
    if cache.lower() == "on":
        try:
            cache_service = get_cache_service()
            cached_summary = cache_service.get_cached_summary(source_lower)
            
            if cached_summary is not None:
                logger.info(f"Returning cached summary for {source_lower}")
                return cached_summary
        except Exception as e:
            # Log cache errors but continue to generate fresh summary
            logger.warning(f"Cache service error (continuing without cache): {str(e)}")
    else:
        logger.info(f"Cache disabled for this request (cache={cache})")

    # Fetch news based on source
    try:
        news_items = []
        source_display_name = ""

        if source_lower == "daily-star":
            source_display_name = "The Daily Star"
            # Fetch 20 articles from Daily Star (synchronous)
            articles = daily_star_scraper.fetch_all_articles_with_details(limit=20)
            # Convert to list of dicts
            news_items = articles

        elif source_lower == "prothom-alo":
            source_display_name = "Prothom Alo"
            # Fetch 20 articles from Prothom Alo (async)
            articles = await prothom_alo_client.fetch_latest(limit=20)
            # Convert Pydantic models to dicts
            news_items = [article.model_dump() for article in articles]

        elif source_lower == "ittefaq":
            source_display_name = "Ittefaq"
            # Fetch 20 articles from Ittefaq (async)
            articles = await ittefaq_client.fetch_latest(limit=20)
            # Convert Pydantic models to dicts
            news_items = [article.model_dump() for article in articles]

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source '{source}'. Valid options: 'daily-star', 'prothom-alo', 'ittefaq'"
            )

        if not news_items:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch news from {source_display_name}. No articles available."
            )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error fetching news from {source}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch news from source. Error: {str(e)}"
        )

    # Generate AI summary
    try:
        # Get the AI service (lazy initialization)
        ai_service = get_ai_summary_service()
        
        # Slice to top 15 items for AI processing
        top_items = news_items[:15]
        
        logger.info(f"Generating AI summary for {len(top_items)} articles from {source_display_name}")
        
        summary = ai_service.generate_daily_summary(top_items)

        # Add metadata to response
        response = {
            **summary,
            "metadata": {
                "source": source_display_name,
                "articles_analyzed": len(top_items),
                "total_articles_fetched": len(news_items)
            }
        }

        # Save to cache (only if cache is enabled)
        if cache.lower() == "on":
            try:
                cache_service = get_cache_service()
                cache_service.save_summary(source_lower, response)
            except Exception as e:
                # Log cache errors but don't fail the request
                logger.warning(f"Failed to save summary to cache: {str(e)}")

        return response

    except Exception as e:
        logger.error(f"AI generation error for {source}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"AI generation failed: {str(e)}"
        )


