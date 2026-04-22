import requests
from bs4 import BeautifulSoup
import json
import time
import random

BASE_URL = "https://webscraper.io/test-sites/e-commerce/static/computers/laptops?page={}"

# 🔥 Realistic mappings
LOCATIONS = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Pune", "Chennai"]
CATEGORIES = ["Semiconductors", "PCB", "Microcontrollers", "Power Supply", "Embedded Systems"]

def generate_rating():
    return f"{round(random.uniform(3.5, 5.0), 1)} stars"

def scrape_page(page):
    url = BASE_URL.format(page)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    products = []

    cards = soup.select(".thumbnail")

    for card in cards:
        name = card.select_one(".title").text.strip()

        products.append({
            "company_name": name,

            # 🔥 Random realistic mapping
            "location": random.choice(LOCATIONS),
            "category": random.choice(CATEGORIES),
            "rating": generate_rating()
        })

    return products


def main():
    all_data = []

    for page in range(1, 6):
        print(f"Scraping page {page}")
        data = scrape_page(page)
        all_data.extend(data)
        time.sleep(1)

    with open("raw_data.json", "w") as f:
        json.dump(all_data, f, indent=4)

    print(f"✅ Scraped {len(all_data)} records")


if __name__ == "__main__":
    main()  