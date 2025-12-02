from pydantic import BaseModel


class ProthomAloNewsItem(BaseModel):
    news_header: str
    image_url: str
    publish_time: str
    section: str
    summary: str | None
    article_url: str
    news_body_text_full: str
