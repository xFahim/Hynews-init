"""Ittefaq news models."""

from pydantic import BaseModel


class IttefaqNewsItem(BaseModel):
    """Model for Ittefaq news article response."""

    title: str
    link: str
    image: str
    summary: str
    category: str
    time: str
    news_body_text_full: str
