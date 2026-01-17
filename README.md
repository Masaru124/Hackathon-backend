# 🏆 Hackathon Aggregator API

A comprehensive API that aggregates hackathons from multiple platforms into a single database. Built with FastAPI, Playwright, and SQLAlchemy.

![Hackathon Aggregator](https://img.shields.io/badge/Hackathon-Aggregator-blue?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3.11+-yellow?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## ✨ Features

- **Multi-Platform Scraping**: Collects hackathons from Devpost, Unstop, MLH, and HackerEarth
- **Automatic Deduplication**: Prevents duplicate entries using stable external IDs
- **Scheduled Updates**: Auto-scrapes every 24 hours with expired hackathon cleanup every 12 hours
- **RESTful API**: Clean FastAPI endpoints for fetching hackathons
- **Self-Ping Mechanism**: Keeps the Render free tier service alive
- **PostgreSQL Support**: Production-ready database configuration
- **CORS Enabled**: Easy integration with frontend applications

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: SQLAlchemy with PostgreSQL
- **Web Scraping**: Playwright + BeautifulSoup4
- **Task Scheduling**: APScheduler
- **Deployment**: Render
- **API Client**: httpx

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database (or use SQLite for local development)
- Playwright browsers installed

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/hackathon-backend.git
   cd hackathon-backend
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**

   ```bash
   playwright install chromium
   ```

5. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your database URL
   ```

6. **Run the application**

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

7. **Access the API**
   - API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/docs

## 📡 API Endpoints

| Method | Endpoint           | Description                                       |
| ------ | ------------------ | ------------------------------------------------- |
| `GET`  | `/hackathons`      | Get all hackathons (optional `?platform=devpost`) |
| `GET`  | `/health`          | Health check endpoint                             |
| `POST` | `/scrape-now`      | Trigger immediate scraping                        |
| `GET`  | `/cleanup-status`  | View expired hackathon statistics                 |
| `POST` | `/cleanup-expired` | Manually delete expired hackathons                |

### Example Usage

```bash
# Get all hackathons
curl http://localhost:8000/hackathons

# Filter by platform
curl http://localhost:8000/hackathons?platform=devpost

# Trigger manual scrape
curl -X POST http://localhost:8000/scrape-now

# Check cleanup status
curl http://localhost:8000/cleanup-status
```

## 📁 Project Structure

```
hackathon-backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application entry point
│   ├── database.py       # SQLAlchemy database configuration
│   ├── models.py         # SQLAlchemy models (Hackathon)
│   ├── crud.py           # Database operations (upsert, delete)
│   ├── scheduler.py      # APScheduler for periodic tasks
│   └── scrappers.py      # Legacy scraper aggregator
├── scrapers/
│   ├── __init__.py
│   ├── aggregator.py     # Multi-source hackathon fetcher
│   ├── devpost.py        # Devpost scraper (17 URLs)
│   ├── unstop.py         # Unstop scraper
│   ├── mlh.py            # MLH scraper
│   └── hackerearth.py    # HackerEarth scraper
├── run_scraper.py        # CLI script for one-time scraping
├── requirements.txt      # Python dependencies
├── render.yaml           # Render deployment configuration
├── .gitignore
├── .env.example
└── README.md
```

## 🔧 Configuration

### Environment Variables

| Variable       | Description                  | Default                     |
| -------------- | ---------------------------- | --------------------------- |
| `DATABASE_URL` | PostgreSQL connection string | `sqlite:///./hackathons.db` |
| `PORT`         | Server port                  | `8000`                      |
| `DEBUG`        | Enable debug mode            | `false`                     |

### Render Deployment

The `render.yaml` file configures automatic deployment to Render:

```yaml
services:
  - type: web
    name: hackathon-app
    env: python
    plan: free
    region: oregon
    branch: main
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase: hackathons-db
    autoDeploy: true
```

## 🧹 Scheduled Jobs

| Job                          | Schedule       | Description                         |
| ---------------------------- | -------------- | ----------------------------------- |
| `scrape_and_update_db`       | Every 24 hours | Fetch hackathons from all platforms |
| `cleanup_expired_hackathons` | Every 12 hours | Remove expired hackathons           |

## 🔍 Scraped Platforms

1. **Devpost** - 17 search URLs including categories like AI, Blockchain, ML, Web3, Fintech, Cybersecurity, Gaming, Healthcare, and more
2. **Unstop** - Status filters (upcoming, ongoing) and mode filters (online, offline)
3. **MLH** - Major League Hacking events for 2026 season
4. **HackerEarth** - Active challenge listings

## 🏗️ Building from Source

```bash
# Build the project
python -m py_compile app/main.py
python -m py_compile scrapers/*.py

# Run tests (if available)
pytest
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Devpost](https://devpost.com) - The largest hackathon platform
- [Unstop](https://unstop.com) - India's largest hackathon platform
- [MLH](https://mlh.io) - Major League Hacking
- [HackerEarth](https://hackerearth.com) - Programming challenges and hackathons

---

## 📊 Contributors


## 📊 Contributors

[![Contributors](https://contrib.rocks/image?repo=Masaru124/hackathon-backend&max=100&cache-bust=1)](
https://github.com/Masaru124/hackathon-backend/graphs/contributors
)
