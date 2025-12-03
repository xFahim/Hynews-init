from fastapi import FastAPI
from dotenv import load_dotenv
from app.api import daily_star, prothom_alo, ittefaq, summary

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Hynews API",
    description="A FastAPI server for fetching news from multiple Bangladeshi news sources",
    version="2.0.0",
)

# Include routers
app.include_router(daily_star.router)
app.include_router(prothom_alo.router)
app.include_router(ittefaq.router)
app.include_router(summary.router)


@app.get("/")
def root():
    return {
        "message": "Hynews API is running!",
        "version": "2.0.0",
        "endpoints": {
            "daily_star": "/dailystar/latest",
            "prothom_alo": "/prothomalo/latest",
            "ittefaq": "/ittefaq/latest",
            "ai_summary": "/summary/{source}",
        },
        "docs": "/docs",
    }
