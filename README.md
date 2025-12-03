<div align="center">

<img src="assets/hylogo.png" alt="Hynews Logo" width="120"/>

# Hynews API

**AI-Powered Bangladeshi News Aggregation API**

A FastAPI-based service that aggregates news from major Bangladeshi news sources and provides intelligent AI-powered daily summaries.

🌐 **Live API**: [https://hynews-init.vercel.app/](https://hynews-init.vercel.app/)

📚 **API Docs**: [https://hynews-init.vercel.app/docs](https://hynews-init.vercel.app/docs)

</div>

---

## 📰 Supported News Sources

<div align="center">

<table>
<tr>
<td align="center" width="33%">
<img src="assets/daily-star.jpg" alt="The Daily Star" width="180" height="100" style="object-fit: contain;"/><br/>
<b>The Daily Star</b><br/>
<code>/dailystar/latest</code>
</td>
<td align="center" width="33%">
<img src="assets/prothom alo.png" alt="Prothom Alo" width="180" height="100" style="object-fit: contain;"/><br/>
<b>Prothom Alo</b><br/>
<code>/prothomalo/latest</code>
</td>
<td align="center" width="33%">
<img src="assets/ittefaq.jpg" alt="Ittefaq" width="180" height="100" style="object-fit: contain;"/><br/>
<b>Ittefaq</b><br/>
<code>/ittefaq/latest</code>
</td>
</tr>
</table>

</div>

## ✨ Features

- 📡 **Multi-source News Aggregation** - Daily Star, Prothom Alo, Ittefaq
- 🤖 **AI Daily Summaries** - Intelligent briefings powered by Google Gemini
- 💾 **Smart Caching** - Supabase-backed caching for faster responses
- 🚀 **Fast & Async** - Non-blocking operations with async/await
- 📝 **Full Article Content** - Complete article text extraction
- 🎯 **Clean REST API** - Well-documented with OpenAPI/Swagger

## 🔗 Try It Now

**Latest News**:
- [Daily Star Latest](https://hynews-init.vercel.app/dailystar/latest)
- [Prothom Alo Latest](https://hynews-init.vercel.app/prothomalo/latest)
- [Ittefaq Latest](https://hynews-init.vercel.app/ittefaq/latest)

**AI Summaries**:
- [Daily Star Summary](https://hynews-init.vercel.app/summary/daily-star)
- [Prothom Alo Summary](https://hynews-init.vercel.app/summary/prothom-alo)
- [Ittefaq Summary](https://hynews-init.vercel.app/summary/ittefaq)

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd Hynews
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Create .env file with:
# GOOGLE_API_KEY=your_gemini_api_key
# SUPABASE_URL=your_supabase_url (optional, for caching)
# SUPABASE_KEY=your_supabase_key (optional, for caching)

# Run server
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## 📡 API Endpoints

### Get Latest News

```http
GET /{source}/latest?limit=10
```

**Sources**: `dailystar`, `prothomalo`, `ittefaq`

**Response Format**:
```json
{
  "status": "success",
  "count": 10,
  "articles": [
    {
      "title": "Article headline",
      "url": "https://...",
      "image": "https://...",
      "date_time": "2024-12-03T...",
      "news_body_text_full": "Complete article text..."
    }
  ]
}
```

### AI Daily Summary ✨

```http
GET /summary/{source}?cache=on
```

**Sources**: `daily-star`, `prothom-alo`, `ittefaq`

**Parameters**:
- `cache` (optional): `on` (default) or `off` to bypass cache

**Response Format**:
```json
{
  "story_of_day": {
    "title": "Most significant story",
    "summary": "Why this story matters..."
  },
  "categories": [
    {
      "category": "Politics",
      "items": ["Key takeaway 1", "Key takeaway 2"]
    }
  ],
  "metadata": {
    "source": "The Daily Star",
    "articles_analyzed": 15
  }
}
```

**Features**:
- Analyzes top 15-20 articles
- Groups stories by category (Politics, Sports, Economy, etc.)
- Identifies "Story of the Day"
- Cached for 24 hours for faster response

## 🛠️ Tech Stack

- **FastAPI** - Modern Python web framework
- **Google Gemini AI** - AI-powered summarization
- **Supabase** - Cloud database for caching
- **BeautifulSoup4 + lxml** - Web scraping
- **httpx** - Async HTTP client

## 📄 License

MIT License - Free to use for personal or commercial purposes.

---

<div align="center">

**Built with ❤️ for the Bangladeshi news ecosystem**

*For educational and research purposes. Please respect the terms of service of news sources.*

</div>
