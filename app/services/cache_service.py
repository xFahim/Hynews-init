"""Cache service for storing daily summaries in Supabase."""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from supabase import create_client, Client

# Set up logging
logger = logging.getLogger(__name__)


class CacheService:
    """Service for caching daily summaries in Supabase."""

    def __init__(self):
        """Initialize the Supabase client with credentials from environment."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY environment variables must be set. "
                "Please add them to your .env file."
            )

        self.client: Client = create_client(supabase_url, supabase_key)
        self.table_name = "daily_summaries"

    def get_cached_summary(self, source: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached summary for the given source and today's date.

        Args:
            source: The news source identifier (e.g., 'daily-star', 'prothom-alo')

        Returns:
            The cached summary content as a dictionary if found, None otherwise
        """
        try:
            # Get today's date in UTC
            today = datetime.now(timezone.utc).date().isoformat()

            logger.info(f"Checking cache for source={source}, date={today}")

            # Query Supabase for cached summary
            response = (
                self.client.table(self.table_name)
                .select("content")
                .eq("source", source)
                .eq("date", today)
                .execute()
            )

            # Check if we got any results
            if response.data and len(response.data) > 0:
                logger.info(f"Cache hit for source={source}, date={today}")
                return response.data[0]["content"]
            
            logger.info(f"Cache miss for source={source}, date={today}")
            return None

        except Exception as e:
            logger.error(f"Error retrieving cached summary: {str(e)}")
            # Return None on error to allow fallback to generating new summary
            return None

    def save_summary(self, source: str, content: Dict[str, Any]) -> bool:
        """
        Save a summary to the cache for the given source and today's date.

        Args:
            source: The news source identifier
            content: The summary content to cache

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Get today's date in UTC
            today = datetime.now(timezone.utc).date().isoformat()

            logger.info(f"Saving summary to cache for source={source}, date={today}")

            # Prepare the data to insert
            data = {
                "source": source,
                "date": today,
                "content": content
            }

            # Insert into Supabase
            # Using upsert to handle potential race conditions gracefully
            response = (
                self.client.table(self.table_name)
                .upsert(data, on_conflict="source,date")
                .execute()
            )

            logger.info(f"Successfully cached summary for source={source}, date={today}")
            return True

        except Exception as e:
            # Log the error but don't fail the request
            # The summary was already generated, so we can still return it
            logger.error(f"Error saving summary to cache: {str(e)}")
            return False


# Lazy-loaded singleton instance
_cache_service_instance: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """
    Get the cache service singleton instance.
    Creates the instance on first call (lazy initialization).

    Returns:
        CacheService instance

    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY are not set in environment
    """
    global _cache_service_instance

    if _cache_service_instance is None:
        _cache_service_instance = CacheService()

    return _cache_service_instance

