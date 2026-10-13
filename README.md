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

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install project dependencies for the backend:

```bash
python -m pip install -r backend/requirements.txt
```

Run the FastAPI app:

```bash
uvicorn backend.app.main:app --reload
```

Open the app in a browser:

```text
http://localhost:8000
```

The frontend is a static JavaScript/HTML/CSS app served from the FastAPI backend. The health endpoint is available at:

```text
http://localhost:8000/api/health
```

## Project Structure

```text
isqa3910/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── crawler.py
├── pages.json
├── search.py
├── README.md
├── requirements.txt
├── .gitignore
└── .venv/
```

Legacy crawler command:

```bash
python crawler.py
```