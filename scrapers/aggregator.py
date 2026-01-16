from .devpost import fetch_hackathons as fetch_devpost_hackathons
from .unstop import fetch_unstop_hackathons
from .mlh import fetch_mlh_hackathons

def fetch_all_hackathons():
    all_hackathons = []

    print("🌐 Fetching hackathons from Devpost...")
    try:
        devpost_hacks = fetch_devpost_hackathons()
        all_hackathons.extend(devpost_hacks)
        print(f"✅ Devpost: {len(devpost_hacks)} hackathons fetched")
    except Exception as e:
        print(f"❌ Devpost fetch failed: {e}")

    print("🌐 Fetching hackathons from Unstop...")
    try:
        unstop_hacks = fetch_unstop_hackathons()
        all_hackathons.extend(unstop_hacks)
        print(f"✅ Unstop: {len(unstop_hacks)} hackathons fetched")
    except Exception as e:
        print(f"❌ Unstop fetch failed: {e}")

    print("🌐 Fetching hackathons from MLH...")
    try:
        mlh_hacks = fetch_mlh_hackathons()
        all_hackathons.extend(mlh_hacks)
        print(f"✅ MLH: {len(mlh_hacks)} hackathons fetched")
    except Exception as e:
        print(f"❌ MLH fetch failed: {e}")

    print(f"🌟 Total hackathons fetched: {len(all_hackathons)}")
    return all_hackathons
