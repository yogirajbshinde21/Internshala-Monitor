import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
from pathlib import Path

def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: config.json not found")
        return None
    except json.JSONDecodeError:
        print("❌ Error: config.json is not valid JSON")
        return None

def load_seen_internships():
    """Load previously seen internship IDs"""
    try:
        # Create data directory if it doesn't exist
        Path('data').mkdir(exist_ok=True)
        
        with open('data/seen_internships.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("⚠️ Warning: seen_internships.json is corrupted, starting fresh")
        return []

def save_seen_internships(internships):
    """Save seen internship IDs to file"""
    try:
        Path('data').mkdir(exist_ok=True)
        with open('data/seen_internships.json', 'w', encoding='utf-8') as f:
            json.dump(internships, f, indent=2)
    except Exception as e:
        print(f"❌ Error saving seen internships: {e}")

def extract_stipend_amount(stipend_text):
    """Extract numeric stipend amount from text like '₹ 5,000 /month'"""
    if not stipend_text or 'not' in stipend_text.lower() or 'unpaid' in stipend_text.lower():
        return 0
    
    # Extract numbers and remove commas
    numbers = re.findall(r'[\d,]+', stipend_text.replace(',', ''))
    if numbers:
        try:
            return int(numbers[0])
        except ValueError:
            return 0
    return 0

def parse_posting_time(time_text):
    """
    Parse posting time text and return days ago as integer.
    Returns:
        - 0 for "Just now" or "Few hours ago"
        - 1 for "1 day ago"
        - Number of days for "X days ago"
        - Number of weeks * 7 for "X weeks ago"
        - 999 for anything older or unparseable
    """
    if not time_text:
        return 999
    
    time_text = time_text.lower().strip()
    
    # Just now or few hours ago - consider as today (0 days)
    if 'just now' in time_text or 'few hours ago' in time_text or 'hour' in time_text:
        return 0
    
    # Extract days
    if 'day' in time_text:
        match = re.search(r'(\d+)\s*day', time_text)
        if match:
            return int(match.group(1))
        return 1  # "1 day ago" or just "day ago"
    
    # Extract weeks
    if 'week' in time_text:
        match = re.search(r'(\d+)\s*week', time_text)
        if match:
            return int(match.group(1)) * 7
        return 7  # "1 week ago" or just "week ago"
    
    # Extract months - treat as too old
    if 'month' in time_text:
        return 999
    
    # Unknown format - treat as too old
    return 999

def is_recent_posting(time_text, max_days_old):
    """Check if posting is within the specified number of days"""
    days_old = parse_posting_time(time_text)
    return days_old <= max_days_old

def matches_preferences(internship_data, config):
    """Check if internship matches user preferences"""
    if not config:
        return True
    
    # Check minimum stipend
    min_stipend = config.get('min_stipend', 0)
    if internship_data['stipend_amount'] < min_stipend:
        return False
    
    # Check location preference
    locations = [loc.lower().strip() for loc in config.get('locations', [])]
    internship_location = internship_data['location'].lower().strip()
    
    if locations:
        location_match = any(
            loc in internship_location or internship_location in loc
            for loc in locations
        )
        if not location_match:
            return False
    
    # Check keywords in title (optional filter)
    keywords = [kw.lower().strip() for kw in config.get('keywords', [])]
    title = internship_data['title'].lower()
    
    if keywords:
        keyword_match = any(kw in title for kw in keywords)
        # If keywords defined but none match, still include (keywords are just preferences)
        # Comment out the next line if you want strict keyword matching
        # if not keyword_match:
        #     return False
    
    return True

def scrape_category(category, headers, config, seen_ids):
    """Scrape a specific internship category"""
    url = f"https://internshala.com/internships/{category}-internship/"
    new_internships = []
    
    try:
        print(f"📡 Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all internship containers - trying multiple possible selectors
        internship_containers = []
        
        # Try different selectors based on Internshala's structure
        possible_selectors = [
            ('div', {'class': 'individual_internship'}),
            ('div', {'class': 'internship_meta'}),
            ('div', {'id': re.compile(r'internship_')}),
        ]
        
        for tag, attrs in possible_selectors:
            internship_containers = soup.find_all(tag, attrs)
            if internship_containers:
                print(f"✅ Found {len(internship_containers)} internships in {category}")
                break
        
        if not internship_containers:
            print(f"⚠️ No internship containers found in {category}")
            return new_internships
        
        for idx, internship in enumerate(internship_containers, 1):
            try:
                # Extract internship ID - try multiple attributes
                internship_id = (
                    internship.get('internshipid') or 
                    internship.get('data-internship-id') or
                    internship.get('id', '').replace('internship_', '')
                )
                
                if not internship_id:
                    # Try to extract from any link
                    link = internship.find('a', href=True)
                    if link and 'detail' in link['href']:
                        internship_id = link['href'].split('/')[-1].split('?')[0]
                
                if not internship_id:
                    continue
                
                if internship_id in seen_ids:
                    continue
                
                # Extract title - try multiple selectors
                title = None
                title_selectors = [
                    ('h3', {'class': re.compile(r'heading')}),
                    ('h3', {}),
                    ('h4', {'class': re.compile(r'profile|title')}),
                    ('a', {'class': re.compile(r'view_detail')}),
                ]
                
                for tag, attrs in title_selectors:
                    title_elem = internship.find(tag, attrs)
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        break
                
                if not title:
                    continue
                
                # Extract company name
                company = "Not specified"
                company_selectors = [
                    ('p', {'class': re.compile(r'company')}),
                    ('div', {'class': re.compile(r'company')}),
                    ('span', {'class': re.compile(r'company')}),
                    ('a', {'class': re.compile(r'link_display_like_text')}),
                ]
                
                for tag, attrs in company_selectors:
                    company_elem = internship.find(tag, attrs)
                    if company_elem:
                        company = company_elem.get_text(strip=True)
                        break
                
                # Extract location
                location = "Location not specified"
                location_selectors = [
                    ('div', {'class': re.compile(r'location')}),
                    ('span', {'class': re.compile(r'location')}),
                    ('a', {'class': re.compile(r'location')}),
                ]
                
                for tag, attrs in location_selectors:
                    location_elem = internship.find(tag, attrs)
                    if location_elem:
                        location = location_elem.get_text(strip=True)
                        break
                
                # Extract stipend
                stipend_text = "Not disclosed"
                stipend_selectors = [
                    ('span', {'class': re.compile(r'stipend')}),
                    ('div', {'class': re.compile(r'stipend')}),
                ]
                
                for tag, attrs in stipend_selectors:
                    stipend_elem = internship.find(tag, attrs)
                    if stipend_elem:
                        stipend_text = stipend_elem.get_text(strip=True)
                        break
                
                stipend_amount = extract_stipend_amount(stipend_text)
                
                # Extract duration
                duration = "Not specified"
                duration_selectors = [
                    ('div', {'class': re.compile(r'duration')}),
                    ('span', {'class': re.compile(r'duration')}),
                ]
                
                for tag, attrs in duration_selectors:
                    duration_elem = internship.find(tag, attrs)
                    if duration_elem:
                        duration = duration_elem.get_text(strip=True)
                        break
                
                # Extract posting time (IMPORTANT for recent filter)
                posting_time = "Unknown"
                days_old = 999
                
                # Look for posting time - usually appears near the end of the internship card
                # Common patterns: "Just now", "Few hours ago", "2 days ago", "1 week ago"
                posting_time_selectors = [
                    ('span', {'class': re.compile(r'status-[a-z]+')}),  # status-success, etc.
                    ('div', {'class': re.compile(r'status')}),
                    ('span', {}),  # Generic span, will look for time patterns
                    ('div', {}),   # Generic div, will look for time patterns
                ]
                
                # Try to find posting time text
                for tag, attrs in posting_time_selectors:
                    time_elems = internship.find_all(tag, attrs, limit=20)
                    for elem in time_elems:
                        text = elem.get_text(strip=True).lower()
                        # Check if this contains time-related keywords
                        if any(keyword in text for keyword in ['ago', 'just now', 'hour', 'day', 'week', 'month']):
                            # Exclude "early applicant" text
                            if 'early applicant' not in text and 'be an early' not in text:
                                posting_time = elem.get_text(strip=True)
                                days_old = parse_posting_time(posting_time)
                                break
                    if posting_time != "Unknown":
                        break
                
                # Check if internship meets recency criteria
                max_days_old = config.get('max_days_old', 999)  # Default: accept all
                if days_old > max_days_old:
                    # Mark as seen but don't include in results
                    seen_ids.append(internship_id)
                    continue
                
                # Extract apply link
                apply_link = ""
                link_elem = internship.find('a', href=True)
                if link_elem:
                    href = link_elem['href']
                    if href.startswith('http'):
                        apply_link = href
                    else:
                        apply_link = f"https://internshala.com{href}" if href.startswith('/') else f"https://internshala.com/{href}"
                
                # Create internship data object
                internship_data = {
                    'id': internship_id,
                    'title': title,
                    'company': company,
                    'location': location,
                    'stipend': stipend_text,
                    'stipend_amount': stipend_amount,
                    'duration': duration,
                    'posting_time': posting_time,
                    'days_old': days_old,
                    'link': apply_link,
                    'category': category,
                    'found_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Check if matches preferences
                if matches_preferences(internship_data, config):
                    new_internships.append(internship_data)
                    seen_ids.append(internship_id)
                    print(f"  ✅ New: {title} at {company} - {location}")
                else:
                    # Still mark as seen but don't notify
                    seen_ids.append(internship_id)
                
            except Exception as e:
                continue
        
        return new_internships
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error for {category}: {e}")
        return new_internships
    except Exception as e:
        print(f"❌ Unexpected error for {category}: {e}")
        return new_internships

def scrape_internshala():
    """Scrape Internshala for new internships across multiple categories"""
    print("🔍 Starting Internshala scraper...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    config = load_config()
    if not config:
        return []
    
    # Get search categories from config
    search_categories = config.get('search_categories', ['full-stack-development'])
    
    all_new_internships = []
    seen_ids = load_seen_internships()
    
    print(f"📋 Searching across {len(search_categories)} categories:")
    for category in search_categories:
        print(f"   • {category}")
    print()
    
    # Scrape each category
    for category in search_categories:
        category_internships = scrape_category(category, headers, config, seen_ids)
        all_new_internships.extend(category_internships)
        
        # Add a small delay between requests to be polite
        if category != search_categories[-1]:  # Don't delay after last category
            import time
            time.sleep(2)
    
    # Save updated seen internships
    if seen_ids:
        save_seen_internships(seen_ids)
    
    print(f"\n📊 Summary: Found {len(all_new_internships)} new matching internships across all categories")
    return all_new_internships

if __name__ == "__main__":
    config = load_config()
    new_opportunities = scrape_internshala()
    
    if new_opportunities:
        print(f"\n🎉 Found {len(new_opportunities)} new internships!")
        for internship in new_opportunities:
            print(f"  - {internship['title']} at {internship['company']}")
            print(f"    📍 {internship['location']} | 💰 {internship['stipend']}")
            print(f"    🔗 {internship['link']}\n")
    else:
        print("\n✅ No new matching internships found.")
