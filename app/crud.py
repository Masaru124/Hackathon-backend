from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from datetime import datetime
import hashlib

from .models import Hackathon


# ---------- HELPERS ---------- #

def safe_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        return None


def generate_external_id(h):
    """
    Stable, platform-scoped unique identity
    """
    if h.get("link"):
        return f"{h['platform']}::{h['link'].strip()}"

    raw = (
        f"{h.get('platform')}|"
        f"{h.get('name')}|"
        f"{h.get('start_date')}|"
        f"{h.get('end_date')}"
    )
    return f"{h.get('platform')}::" + hashlib.sha256(raw.encode()).hexdigest()


# ---------- CORE LOGIC ---------- #

def upsert_hackathons(db: Session, hackathons: list):
    # Get row count with error handling
    try:
        existing_count = db.query(Hackathon).count()
    except OperationalError:
        print("⚠️ Could not get existing row count (connection issue), proceeding anyway...")
        existing_count = "unknown"
    
    print("📦 Rows already in DB:", existing_count)

    # ✅ DEDUPE INPUT FIRST (CRITICAL)
    unique_input = {}
    for h in hackathons:
        eid = generate_external_id(h)
        unique_input[eid] = h  # last one wins

    hackathons = list(unique_input.values())

    inserted = 0
    updated = 0
    skipped = 0

    # ✅ USE external_id as the ONLY identity
    existing = {
        h.external_id: h
        for h in db.query(Hackathon).all()
    }

    for h in hackathons:
        external_id = generate_external_id(h)
        existing_row = existing.get(external_id)

        if existing_row:
            changed_fields = []

            for field in ["prize", "participants", "location", "start_date", "end_date", "image_url"]:
                new_val = h.get(field)
                if new_val and getattr(existing_row, field) != new_val:
                    setattr(existing_row, field, new_val)
                    changed_fields.append(field)

            if changed_fields:
                updated += 1
                print(f"🔄 Updated '{existing_row.name}' - fields: {', '.join(changed_fields)}")

            skipped += 1
            continue

        # ✅ INSERT NEW
        hack = Hackathon(
            external_id=external_id,
            name=h.get("name", "Unknown"),
            platform=h.get("platform", "Unknown"),
            link=h.get("link"),
            start_date=safe_date(h.get("start_date")),
            end_date=safe_date(h.get("end_date")),
            location=h.get("location"),
            prize=h.get("prize"),
            participants=h.get("participants"),
            image_url=h.get("image_url"),
        )

        db.add(hack)
        existing[external_id] = hack
        inserted += 1

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        print("❌ DB commit failed:", e)
        raise

    print(f"✅ Inserted: {inserted}")
    print(f"🔄 Updated: {updated}")
    print(f"⚠️ Skipped: {skipped}")

    return {
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "total": len(hackathons),
    }


def delete_expired_hackathons(db: Session) -> int:
    """
    Delete hackathons where end_date < current date.
    Returns the count of deleted hackathons.
    """
    from datetime import date
    now = date.today()
    
    # Only delete if end_date is set and is before today
    expired = db.query(Hackathon).filter(
        Hackathon.end_date.isnot(None),
        Hackathon.end_date < now
    )
    
    count = expired.count()
    if count > 0:
        expired.delete(synchronize_session=False)
        db.commit()
        print(f"🧹 Deleted {count} expired hackathons")
    else:
        print("🧹 No expired hackathons to delete")
    
    return count

