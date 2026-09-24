import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time


START_URL = "https://docs.python.org/3/tutorial/"
MAX_PAGES = 10

pages_to_visit = [START_URL]
visited_pages = set()
collected_pages = []


def is_same_domain(url):
    """Only allow links from docs.python.org."""
    return urlparse(url).netloc == "docs.python.org"


while pages_to_visit and len(visited_pages) < MAX_PAGES:

    current_url = pages_to_visit.pop(0)

    if current_url in visited_pages:
        continue

    print(f"Crawling: {current_url}")

    try:
        response = requests.get(current_url, timeout=10)

        if response.status_code != 200:
            print(f"  Skipped - status code {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Get the page title
        if soup.title:
            title = soup.title.get_text(strip=True)
        else:
            title = "No title"

        # Get page text
        text = soup.get_text(" ", strip=True)

        # Save what we found
        collected_pages.append({
            "title": title,
            "url": current_url,
            "text": text
        })

        visited_pages.add(current_url)

        print(f"  Title: {title}")
        print(f"  Characters collected: {len(text)}")

        # Find links on this page
        for link in soup.find_all("a"):

            href = link.get("href")

            if not href:
                continue

            # Turn relative links into complete URLs
            full_url = urljoin(current_url, href)

            # Remove #sections from URLs
            full_url = full_url.split("#")[0]

            # Only follow Python documentation links
            if is_same_domain(full_url):

                if (
                    full_url not in visited_pages
                    and full_url not in pages_to_visit
                ):
                    pages_to_visit.append(full_url)

        # Be polite to the server
        time.sleep(0.5)

    except requests.RequestException as error:
        print(f"  Error: {error}")


# Save everything we collected
with open("pages.json", "w", encoding="utf-8") as file:
    json.dump(collected_pages, file, indent=4, ensure_ascii=False)


print()
print("=" * 50)
print(f"Finished crawling {len(collected_pages)} pages.")
print("Results saved to pages.json")