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
    "https://www.picklesburgh.com/",
    "https://www.pghtacofest.com/",
    "https://pittsburghrestaurantweek.com/",
    "https://littleitalydays.com/",
    "https://bananasplitfest.com/"
]

# List to hold the scraped content
content_list = []

for url in urls:
    # Try to scrape with Selenium (for dynamic content)
    try:
        driver.get(url)
        
        # Wait for the page content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        # Click on expandable sections if present
        try:
            expand_buttons = driver.find_elements(By.CSS_SELECTOR, '.expandable-button')  # Adjust selector if needed
            for button in expand_buttons:
                button.click()
                WebDriverWait(driver, 2).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '.expanded-content'))  # Adjust selector if needed
                )
        except Exception as e:
            print(f"No expandable sections found or error: {e}")
        
        # Use BeautifulSoup to parse the page content
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        main_content = soup.find('main') or soup.find('body')
        
        if main_content:
            title = soup.title.string if soup.title else 'No Title'
            content_text = main_content.get_text(separator=' ', strip=True)
            content_list.append({"title": title, "content": content_text})
        else:
            # Fallback to static scraping if dynamic content fails
            print(f"Falling back to static scrape for: {url}")
            content_text = scrape_text(url)
            content_list.append({"title": f"Static scrape of {url}", "content": content_text})

    except Exception as e:
        print(f"Error scraping {url}: {e}")

# Save the list of dictionaries to a JSON file
with open('music_and_culture_events_content.json', 'w', encoding='utf-8') as file:
    json.dump(content_list, file, ensure_ascii=False, indent=4)

print("Content successfully scraped and saved to music_and_culture_events_content.json")

# Close the browser
driver.quit()
