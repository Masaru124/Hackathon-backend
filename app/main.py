import asyncio
from fastapi import FastAPI
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from .crud import get_hackathons, upsert_hackathons
from .scheduler import start_scheduler
from scrapers.aggregator import fetch_all_hackathons
import httpx
from fastapi import FastAPI, Depends

from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hackathon Aggregator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <-- allows requests from any frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    start_scheduler()
    # Start the self-ping background task
    asyncio.create_task(self_ping())

# Self-ping task
async def self_ping():
    url = "https://hackathon-backend-3stq.onrender.com/health"
    async with httpx.AsyncClient() as client:
        while True:
            try:
                resp = await client.get(url)
                print(f"Self-ping status: {resp.status_code}")
            except Exception as e:
                print(f"Self-ping failed: {e}")
            await asyncio.sleep(5 * 60)  # 5 minutes

@app.get("/hackathons")
def fetch_hackathons(
    platform: str | None = None,
    db: Session = Depends(get_db)
):
    return get_hackathons(db, platform=platform)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/scrape-now")
def scrape_now(db: Session = Depends(get_db)):
    data = fetch_all_hackathons()
    added = upsert_hackathons(db, data)
    return {"status": "done", "added": added}
