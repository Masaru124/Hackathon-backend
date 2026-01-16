from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import time
import random

MLH_URL = "https://mlh.io/seasons/2026/events"


def fetch_mlh_hackathons():
    hackathons = {}
    max_retries = 3
    
    for attempt in range(max_retries):
        print(f"\n🔄 Attempt {attempt + 1}/{max_retries}...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--window-size=1920,1080",
                ]
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
            )
            
            page = context.new_page()
            
            # Store captured API responses
            api_data = []
            
            # Capture all API responses
            def handle_response(response):
                url = response.url
                if 'api' in url.lower() or 'events' in url.lower() or 'json' in url.lower():
                    try:
                        content_type = response.headers.get('content-type', '')
                        if 'application/json' in content_type or url.endswith('.json'):
                            data = response.json()
                            api_data.append({'url': url, 'data': data})
                            print(f"📡 Captured API response: {url}")
                    except:
                        pass
            
            page.on('response', handle_response)
            
            page.set_extra_http_headers({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            })
            
            try:
                print(f"Navigating to {MLH_URL}...")
                page.goto(
                    MLH_URL, 
                    timeout=60000, 
                    wait_until="domcontentloaded"
                )
                
                # Wait for network to be idle (all API calls complete)
                print("Waiting for network to settle...")
                try:
                    page.wait_for_load_state("networkidle", timeout=30000)
                except:
                    print("Network not fully idle, continuing anyway...")
                
                # Additional wait for JavaScript rendering
                time.sleep(3)
                
                # Check page title
                title = page.title()
                print(f"Page title: {title}")
                
                # Check if we captured any API data
                print(f"\n📡 Captured {len(api_data)} API responses")
                
                # Try to extract hackathon data from API responses
                for api_response in api_data:
                    try:
                        data = api_response['data']
                        
                        # Check if it contains events/hackathons
                        if isinstance(data, dict):
                            for key in data:
                                if 'event' in key.lower() or 'hackathon' in key.lower():
                                    print(f"Found potential data in key: {key}")
                                    events = data[key]
                                    if isinstance(events, list) and len(events) > 0:
                                        print(f"Found {len(events)} events!")
                                        for event in events:
                                            if isinstance(event, dict):
                                                name = event.get('name', event.get('title', 'Unknown'))
                                                link = event.get('link', event.get('url', event.get('website', '')))
                                                date = event.get('date', event.get('start_date', event.get('startDate', 'TBD')))
                                                location = event.get('location', event.get('city', 'TBD'))
                                                image = event.get('image', event.get('logo', event.get('banner', None)))
                                                
                                                if link and not link.startswith('http'):
                                                    link = 'https://mlh.io' + link
                                                if image and not image.startswith('http'):
                                                    image = 'https:' + image
                                                
                                                if link:
                                                    hackathons[link] = {
                                                        "name": name,
                                                        "platform": "MLH",
                                                        "location": location,
                                                        "date": date,
                                                        "link": link,
                                                        "image_url": image,
                                                    }
                                                    
                                                    print(f"Name: {name}\nDate: {date}\nLink: {link}\n{'-'*40}")
                        
                        elif isinstance(data, list):
                            print(f"Found list with {len(data)} items")
                            for item in data[:5]:
                                print(f"  Item: {str(item)[:200]}")
                    
                    except Exception as e:
                        print(f"Error parsing API response: {e}")
                        continue
                
                # If no data from API, try to find event links on the page
                if not hackathons:
                    print("\nNo API data found, looking for event links on page...")
                    html = page.content()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for all links that might be event pages
                    all_links = soup.find_all('a', href=True)
                    event_links = []
                    
                    for link in all_links:
                        href = link.get('href', '')
                        if '/events/' in href and href not in event_links:
                            full_link = href if href.startswith('http') else 'https://mlh.io' + href
                            event_links.append(full_link)
                    
                    print(f"Found {len(event_links)} event links")
                    
                    # Visit each event page
                    for link in event_links[:10]:  # Limit to 10
                        try:
                            print(f"\nVisiting: {link}")
                            page.goto(link, timeout=30000, wait_until="domcontentloaded")
                            time.sleep(2)
                            
                            event_html = page.content()
                            event_soup = BeautifulSoup(event_html, 'html.parser')
                            
                            # Extract event details
                            title_el = event_soup.find('h1')
                            title = title_el.get_text(strip=True) if title_el else "Unknown"
                            
                            # Look for date
                            date = "TBD"
                            for pattern in ['[class*="date"]', '[class*="time"]', 'time']:
                                el = event_soup.select_one(pattern)
                                if el:
                                    date = el.get_text(strip=True)
                                    break
                            
                            # Look for location
                            location = "TBD"
                            for pattern in ['[class*="location"]', '[class*="city"]', '[class*="venue"]']:
                                el = event_soup.select_one(pattern)
                                if el:
                                    location = el.get_text(strip=True)
                                    break
                            
                            # Look for image
                            image_url = None
                            img_el = event_soup.find('img')
                            if img_el:
                                image_url = img_el.get('src') or img_el.get('data-src')
                                if image_url and not image_url.startswith('http'):
                                    image_url = 'https:' + image_url
                            
                            hackathons[link] = {
                                "name": title,
                                "platform": "MLH",
                                "location": location,
                                "date": date,
                                "link": link,
                                "image_url": image_url,
                            }
                            
                            print(f"Name: {title}\nLocation: {location}\nDate: {date}\nLink: {link}\n{'-'*40}")
                            
                        except Exception as e:
                            print(f"Error visiting {link}: {e}")
                            continue
                
                browser.close()
                break
                
            except Exception as e:
                print(f"⚠️ Error on attempt {attempt + 1}: {e}")
                browser.close()
                if attempt < max_retries - 1:
                    wait_time = random.uniform(5, 10)
                    print(f"Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                continue

    print(f"\n✅ TOTAL MLH hackathons scraped: {len(hackathons)}")
    return list(hackathons.values())


if __name__ == "__main__":
    fetch_mlh_hackathons()

