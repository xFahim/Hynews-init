"""Daily Star news models."""

from pydantic import BaseModel
from typing import Optional


class DailyStarArticle(BaseModel):
    """Model for Daily Star article response."""

    title: str
    url: str
    heading: str
    date_time: str
    image: str
    news_body_text_full: str


