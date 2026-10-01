import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
import re


START_URL = "https://www.gpsne.org/"
MAX_PAGES = 10

pages_to_visit = [START_URL]
visited_pages = set()
collected_pages = []


def is_same_domain(url):
    """Only allow links from gpsne.org."""
    return urlparse(url).netloc in ["www.gpsne.org", "gpsne.org"]

def extract_embedded_content(raw_html, current_url):
    """
    Extract HTML content that is stored inside JSON-like data
    in the webpage source.

    Some websites, such as the Gretna site, store the actual
    page content as escaped HTML inside "html" fields.
    """

    embedded_text = []
    embedded_links = []

    # Find values that look like:
    # "html":"<p>Some content...</p>"
    matches = re.findall(
        r'\\"html\\":\\"(.*?)\\"(?=,\\"|\})',
        raw_html,
        re.DOTALL
    )

    for escaped_html in matches:
        try:
            # Decode escaped characters such as \" and \n
            decoded_html = bytes(
                escaped_html,
                "utf-8"
            ).decode("unicode_escape")

            inner_soup = BeautifulSoup(
                decoded_html,
                "html.parser"
            )

            # Extract the readable text
            text = inner_soup.get_text(" ", strip=True)

            if text:
                embedded_text.append(text)

            # Extract links from the embedded HTML
            for link in inner_soup.find_all("a"):
                href = link.get("href")

                if not href:
                    continue

                link_text = link.get_text(" ", strip=True)

                full_url = urljoin(current_url, href)

                embedded_links.append({
                    "text": link_text,
                    "url": full_url
                })

        except Exception as error:
            print(f"  Could not parse embedded content: {error}")

    return embedded_text, embedded_links

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

        embedded_text, embedded_links = extract_embedded_content(
            response.text,
            current_url
        )

        # Get the page title
        if soup.title:
            title = soup.title.get_text(strip=True)
        else:
            title = "No title"

        # Get page text
        text = soup.get_text(" ", strip=True)

        # Add page-specific content found inside embedded HTML
        if embedded_text:
            text += " " + " ".join(embedded_text)

        # Collect all links found on this page
        page_links = []

        for link in soup.find_all("a"):
            href = link.get("href")

            if not href:
                continue

            link_text = link.get_text(" ", strip=True)

            # Convert relative links to full URLs
            full_url = urljoin(current_url, href)

            page_links.append({
                "text": link_text,
                "url": full_url
            })

        # Add links discovered inside embedded page content
        page_links.extend(embedded_links)

        # Save what we found
        collected_pages.append({
            "title": title,
            "url": current_url,
            "text": text,
            "links": page_links
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