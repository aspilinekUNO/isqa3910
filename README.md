# MPS Information Retrieval Prototype

Student project developing an information retrieval system for Millard Public Schools. The goal is to help MPS staff find relevant district resources through a simple question-based interface.

## Current Progress

- Developed and tested an initial Python web crawler.
- Confirmed that the live MPS website blocks standard automated requests with an HTTP `403` response.
- Obtained a local parsed snapshot of MPS website content for development and testing.
- Developed a TF-IDF retrieval prototype capable of searching the parsed MPS document collection.
- Developed an initial curated MPS information tree containing resource categories, subcategories, descriptions, keywords, staff intents, and source URLs.
- Implemented information-tree search using natural-language user queries.
- Created a FastAPI backend and static JavaScript/HTML/CSS frontend.
- Connected the frontend to the retrieval backend through `/api/search`.
- Search results display ranked MPS resources with descriptions and links to the original sources.

## Current Architecture

```text
User Question
     ↓
Web Interface
     ↓
FastAPI /api/search
     ↓
Information Tree Search
     ↓
Curated MPS Resources
     ↓
Ranked Results
     ↓
Original MPS Resource Links
```

The project also contains a larger parsed MPS document collection that can be searched separately. Future work will investigate combining the curated information tree with full-document retrieval.

## Data Sources

### Curated Information Tree

`mps_resources.json` contains curated MPS resources with fields such as:

- Category and subcategory
- Resource name and type
- Description
- Search keywords
- Staff intent
- Original source URL

`mps_data.py` provides helper functions for reading and using this resource data.

### Parsed MPS Content

A local parsed-content export contains MPS webpages, Google Drive content, PDFs, calendars, Office documents, and other resources.

The dataset is used locally and is excluded from Git.

### Legacy Web Crawler

`crawler.py` was developed during early prototyping to investigate website ingestion. It successfully crawls websites that permit normal automated requests. Direct requests to the live MPS website currently return HTTP `403`, so development has shifted to the provided local MPS content snapshot.

## Setup

Create a virtual environment.

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install project dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the FastAPI app:

```bash
uvicorn backend.app.main:app --reload
```

Open the application:

```text
http://localhost:8000
```

FastAPI API documentation is available at:

```text
http://localhost:8000/docs
```

The backend health endpoint is available at:

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
├── frontend/
│   ├── assets/
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── crawler.py
├── mps_data.py
├── mps_resources.json
├── mps_pages.json
├── search.py
├── README.md
├── requirements.txt
└── .gitignore
```

## Search

The current application searches the curated information tree and returns the MPS resources that most closely match the user's question.

Example queries include:

- `Where can I find employee benefits?`
- `I need help with my computer`
- `I need the sports physical form`
- `Where is the administrative calendar?`

The retrieval system currently uses TF-IDF and cosine similarity to rank resources. Generative AI is not currently required for resource retrieval.

## Planned Work

- Expand the curated information tree with additional MPS resources.
- Test retrieval against realistic staff questions.
- Improve handling of low-confidence or ambiguous searches.
- Integrate information-tree retrieval with the larger parsed MPS document collection.
- Improve retrieval from long documents through section/chunk-based indexing.
- Determine how source authority and resource scope should affect ranking.
- Continue accessibility and usability testing.
- Refine the interface and prepare project documentation for MPS handoff.

## test_search.py
A test file for return accuracy and relevance

Baseline:
Overall:    8/13
Supported:  6/6
Irrelevant: 2/7

TF-IDF intent gate:
Overall:    8/13
Supported:  5/6
Irrelevant: 3/7

Semantic:
Overall:    12/13 passed
Supported:  5/6 passed
Irrelevant: 7/7 passed
