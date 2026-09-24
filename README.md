# MPS Chatbot / Information Retrieval Prototype

Student project for developing an information retrieval system for Millard Public Schools. The eventual goal is to help MPS staff quickly find information and resources across MPS websites.

## Current Progress

- Created an initial Python web crawler.
- Successfully tested downloading, parsing, and extracting links from `example.com`.
- Expanded the crawler to follow links and save collected page information to `pages.json`.
- Tested the crawler using the Python documentation website.
- Discovered that direct requests to `mpsomaha.org` return a `403` response due to the site's anti-bot protection.
- Added `.gitignore` to exclude the virtual environment and other unnecessary files.
- Added `requirements.txt` so dependencies can be recreated.

## Next Steps

1. Build a simple retrieval/search system using the collected page data.
2. Test retrieval using the Python documentation dataset.
3. Determine an approved method for accessing MPS website content.
4. Eventually test retrieval against real MPS resources.
5. Add AI-generated answers only after basic retrieval is working.

## Important Finding

The crawler works on other websites, but `mpsomaha.org` currently returns HTTP `403` to normal Python requests. Ask the MPS sponsor/IT team whether there is an approved way to access website content programmatically, such as a sitemap, CMS/API access, or another data source.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the crawler:

```powershell
python crawler.py
```