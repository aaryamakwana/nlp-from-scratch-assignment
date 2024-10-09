import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to scrape static content using BeautifulSoup
def scrape_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ensure GUI-less operation
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize Selenium WebDriver with Chrome in headless mode
driver = webdriver.Chrome(service=Service(), options=chrome_options)

# List of URLs to scrape (Music and Culture events)
urls = [
    "https://www.pittsburghsymphony.org/",
    "https://pittsburghopera.org/",
    "https://trustarts.org/",
    "https://carnegiemuseums.org/",
    "https://www.heinzhistorycenter.org/",
    "https://www.thefrickpittsburgh.org/",
    "https://www.visitpittsburgh.com/events-festivals/food-festivals/",
    "https://www.picklesburgh.com/",
    "https://www.pghtacofest.com/",
    "https://pittsburghrestaurantweek.com/",
    "https://littleitalydays.com/",
    "https://bananasplitfest.com/"
]

# List to hold the scraped content
content_list = []

def scrape_page(url):
    """Scrapes content from a given page using BeautifulSoup after Selenium loads it."""
    driver.get(url)
    
    # Wait for the page content to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body'))
    )
    
    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    main_content = soup.find('main') or soup.find('body')
    
    if main_content:
        title = soup.title.string if soup.title else 'No Title'
        content_text = main_content.get_text(separator=' ', strip=True)
        return {"title": title, "content": content_text}
    return None

def extract_sublinks(soup, base_url):
    """Extracts all sublinks from the main page."""
    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if href.startswith('/'):  # Relative link
            full_url = base_url + href
        elif base_url in href:  # Full link within the base domain
            full_url = href
        else:
            continue
        links.append(full_url)
    return links

# Start scraping each URL and its sublinks
for url in urls:
    # Start by scraping the main page
    content = scrape_page(url)
    if content:
        content_list.append(content)

    # Extract sublinks from the main page
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    base_url = url.rstrip('/')  # Remove trailing slash
    sublinks = extract_sublinks(soup, base_url)

    # Scrape each subpage
    for sublink in sublinks:
        sub_content = scrape_page(sublink)
        if sub_content:
            content_list.append(sub_content)

# Save the list of dictionaries to a JSON file
with open('music_and_culture_events_content.json', 'w', encoding='utf-8') as file:
    json.dump(content_list, file, ensure_ascii=False, indent=4)

print("Content successfully scraped and saved to music_and_culture_events_content.json")

# Close the browser
driver.quit()
