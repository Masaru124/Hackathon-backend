# app/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from scrapers.aggregator import fetch_all_hackathons
from app.database import SessionLocal
from app.crud import upsert_hackathons, delete_expired_hackathons

def scrape_and_update_db():
    print("🔄 Running scheduled scrape...")
    db = SessionLocal()
    try:
        hackathons = fetch_all_hackathons()
        added = upsert_hackathons(db, hackathons)
        print(f"✅ Scheduled scrape done. {added} new hackathons added.")
    finally:
        db.close()

def cleanup_expired_hackathons():
    """Scheduled job to delete expired hackathons"""
    print("🧹 Running scheduled cleanup of expired hackathons...")
    db = SessionLocal()
    try:
        count = delete_expired_hackathons(db)
        print(f"✅ Cleanup complete. {count} expired hackathons deleted.")
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Run scraping every 24 hours
    scheduler.add_job(scrape_and_update_db, "interval", hours=24, id="daily_scrape")
    # Run cleanup every 12 hours (adjust as needed)
    scheduler.add_job(cleanup_expired_hackathons, "interval", hours=12, id="cleanup_expired")
    scheduler.start()
    print("⏰ Scheduler started - scraping every 24h, cleanup every 12h.")

