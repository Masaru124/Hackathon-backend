from playwright.sync_api import sync_playwright
import time

BASE_URL = "https://unstop.com/hackathons"

FILTER_URLS = [
    # Status filters
    "https://unstop.com/hackathons?status=upcoming",
    "https://unstop.com/hackathons?status=ongoing",
    # Mode filters
    "https://unstop.com/hackathons?mode=online",
    "https://unstop.com/hackathons?mode=offline"  
      "https://unstop.com/hackathons?mode=hybrid",
    # Eligibility filters
    "https://unstop.com/hackathons?eligibility=everyone",
    "https://unstop.com/hackathons?eligibility=college",
    "https://unstop.com/hackathons?eligibility=high-school",
    "https://unstop.com/hackathons?eligibility=professionals",
    # Category search filters
    "https://unstop.com/hackathons?search=ai",
    "https://unstop.com/hackathons?search=blockchain",
    "https://unstop.com/hackathons?search=machine+learning",
    "https://unstop.com/hackathons?search=web3",
    "https://unstop.com/hackathons?search=fintech",
    "https://unstop.com/hackathons?search=cybersecurity",
    "https://unstop.com/hackathons?search=robotics",
    "https://unstop.com/hackathons?search=gaming",
    "https://unstop.com/hackathons?search=data+science",
    "https://unstop.com/hackathons?search=cloud",
    "https://unstop.com/hackathons?search=iot",
    "https://unstop.com/hackathons?search=vr",
    "https://unstop.com/hackathons?search=ar",
    "https://unstop.com/hackathons?search=healthcare",
    "https://unstop.com/hackathons?search=social+impact",
    "https://unstop.com/hackathons?search=sustainability",
    "https://unstop.com/hackathons?search=education",
    "https://unstop.com/hackathons?search=crypto",
    "https://unstop.com/hackathons?search=defi",
    "https://unstop.com/hackathons?search=nft",
    "https://unstop.com/hackathons?search=metaverse",
    "https://unstop.com/hackathons?search=quantum",
    "https://unstop.com/hackathons?search=automation",
    "https://unstop.com/hackathons?search=devops",
    "https://unstop.com/hackathons?search=backend",
    "https://unstop.com/hackathons?search=frontend",
    "https://unstop.com/hackathons?search=fullstack",
    "https://unstop.com/hackathons?search=mobile",
    "https://unstop.com/hackathons?search=design",
    "https://unstop.com/hackathons?search=product",
    "https://unstop.com/hackathons?search=management",
    "https://unstop.com/hackathons?search=finance",
    "https://unstop.com/hackathons?search=marketing",
    "https://unstop.com/hackathons?search=social",
]

def fetch_unstop_hackathons():
    hackathons = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for url in FILTER_URLS:
            print(f"\n🔍 Scraping: {url}")
            page.goto(url, timeout=60000)
            page.wait_for_timeout(4000)

            last_count = 0
            idle_scrolls = 0

            while idle_scrolls < 3:
                # Scroll to bottom
                page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                time.sleep(2)

                # Grab all hackathon links
                links = page.locator("a[href^='/hackathons/']")
                count = links.count()

                if count == last_count:
                    idle_scrolls += 1
                else:
                    idle_scrolls = 0

                last_count = count

                # Extract hackathons
                for i in range(count):
                    link = links.nth(i).get_attribute("href")
                    if not link:
                        continue
                    full_link = "https://unstop.com" + link
                    if full_link in hackathons:
                        continue
                    title = links.nth(i).inner_text().strip()

                    # Try to extract image URL from parent card
                    image_url = None
                    try:
                        # Get the parent card element
                        card = links.nth(i).locator("..")
                        img_el = card.locator("img")
                        if img_el.count() > 0:
                            image_url = img_el.get_attribute("src") or img_el.get("data-src") or img_el.get("data-image")
                            if image_url and not image_url.startswith("http"):
                                image_url = "https://unstop.com" + image_url
                    except Exception:
                        pass

                    hackathons[full_link] = {
                        "name": title,
                        "platform": "Unstop",
                        "location": "Online" if "online" in url else "Offline",
                        "link": full_link,
                        "image_url": image_url,
                    }

            print(f"📦 Collected so far: {len(hackathons)}")

        browser.close()

    print(f"\n✅ TOTAL Unstop hackathons scraped: {len(hackathons)}")
    return list(hackathons.values())


if __name__ == "__main__":
    fetch_unstop_hackathons()

