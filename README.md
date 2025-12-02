# Hynews API 🗞️

A FastAPI-based news aggregation service that provides clean JSON responses for news articles from popular Bangladeshi news platforms. We handle all the heavy lifting—API integration, web scraping, and data normalization—so you get consistent, structured news data.

## 🎯 Overview

Hynews aggregates news from multiple Bangladeshi news sources through a unified REST API. Each source is handled differently based on availability:

- **API Integration**: For sources with public APIs
- **Web Scraping**: For sources requiring HTML parsing
- **Hybrid Approach**: Combining both methods for complete data

All complexity is abstracted away, delivering clean, normalized JSON responses.

## ✨ Features

- **Multi-source Support**: Daily Star, Prothom Alo, Ittefaq (more coming soon)
- **Async Operations**: Fast, non-blocking requests using `httpx`
- **Full Article Content**: Complete article body text extraction
- **Configurable Parameters**: Control article count, image dimensions, and limits
- **Clean REST API**: Well-documented endpoints with OpenAPI/Swagger
- **Error Handling**: Graceful degradation and comprehensive error responses

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Hynews

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### Root

```http
GET /
```

Returns API information and available endpoints.

---

### Daily Star

```http
GET /dailystar/latest?limit=10
```

**Parameters:**

- `limit` (optional): Number of articles (1-100, default: 10)

**Response:**

```json
{
  "status": "success",
  "count": 10,
  "limit": 10,
  "articles": [
    {
      "title": "Article title",
      "url": "https://www.thedailystar.net/...",
      "heading": "Article heading",
      "date_time": "Published date",
      "image": "Image URL",
      "news_body_text_full": "Full article text..."
    }
  ]
}
```

---

### Prothom Alo

```http
GET /prothomalo/latest?limit=10
```

**Parameters:**

- `limit` (optional): Number of articles (1-100, default: 10)

**Response:**

```json
[
  {
    "news_header": "Article headline",
    "image_url": "https://images.assettype.com/...",
    "publish_time": "2024-12-02T10:30:00Z",
    "section": "National",
    "summary": "Article summary",
    "article_url": "https://www.prothomalo.com/...",
    "news_body_text_full": "Full article text..."
  }
]
```

---

### Ittefaq

```http
GET /ittefaq/latest?limit=10
```

**Parameters:**

- `limit` (optional): Number of articles to return (1-100)

**Response:**

```json
[
  {
    "title": "Article title",
    "link": "https://www.ittefaq.com.bd/...",
    "image": "https://cdn.ittefaqbd.com/...",
    "summary": "Article summary",
    "category": "Politics",
    "time": "Publication time",
    "news_body_text_full": "Full article text..."
  }
]
```

## 🏗️ Project Structure

```
Hynews/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API route handlers
│   │   ├── daily_star.py       # Daily Star endpoints
│   │   ├── prothom_alo.py      # Prothom Alo endpoints
│   │   └── ittefaq.py          # Ittefaq endpoints
│   ├── models/                 # Pydantic models
│   │   ├── daily_star.py       # Daily Star data models
│   │   ├── prothom_alo.py      # Prothom Alo data models
│   │   └── ittefaq.py          # Ittefaq data models
│   └── services/               # Business logic & scrapers
│       ├── scraper.py          # Daily Star scraper
│       ├── prothom_alo.py      # Prothom Alo API client
│       ├── ittefaq.py          # Ittefaq API client
│       └── image_extractor.py  # Image extraction utility
├── requirements.txt
└── README.md
```

## 🛠️ Tech Stack

- **FastAPI**: Modern, high-performance web framework
- **Uvicorn**: Lightning-fast ASGI server
- **httpx**: Async HTTP client for API requests
- **requests**: HTTP library for synchronous requests
- **BeautifulSoup4**: HTML parsing and web scraping
- **lxml**: High-performance XML/HTML parser
- **Pydantic**: Data validation and settings management

## 📰 Supported News Sources

| Source           | Method         | Status     |
| ---------------- | -------------- | ---------- |
| **Daily Star**   | Web Scraping   | ✅ Active  |
| **Prothom Alo**  | API + Scraping | ✅ Active  |
| **Ittefaq**      | API + Scraping | ✅ Active  |
| **More sources** | Coming Soon    | 🚧 Planned |

## 🔧 Development

### Adding a New News Source

1. **Create Service**: Add a client/scraper in `app/services/`
2. **Define Model**: Create Pydantic model in `app/models/`
3. **Create Router**: Add API routes in `app/api/`
4. **Register**: Include router in `app/main.py`

### Error Handling

- **500**: Internal server errors (scraping/parsing failures)
- **502**: Upstream API failures (external services unreachable)
- **4xx**: Client errors (invalid parameters)

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Add new news sources
- Improve existing scrapers
- Enhance error handling
- Update documentation

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🙏 Acknowledgments

Built with ❤️ for the Bangladeshi news ecosystem.

---

**Note**: This project is for educational and research purposes. Please respect the terms of service of the news sources being accessed.
