import csv
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel
from search import search_resources, check_query_safety

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
PROJECT_ROOT = BASE_DIR.parent

app = FastAPI(
    title="Project Backend",
    version="0.1.0",
    description="Starter FastAPI backend for a Python + JavaScript web app.",
)

class SearchRequest(BaseModel):
    query: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/schools")
def get_schools() -> list[dict[str, str]]:
    schools_csv = PROJECT_ROOT / "data" / "schools.csv"
    schools: list[dict[str, str]] = []

    with schools_csv.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if not row:
                continue

            name, url = row[0], row[1] if len(row) > 1 else ""
            name = name.strip()
            url = url.strip()

            if not name or not url:
                continue
            if "school name" in name.lower() and "website" in url.lower():
                continue

            schools.append({"name": name, "url": url})

    return schools


@app.post("/api/search")
def search_mps(request: SearchRequest):
    allowed, reason = check_query_safety(request.query)
    if not allowed:
        return {
            "query": request.query,
            "blocked": True,
            "reason": reason,
            "results": []
        }
    
    results = search_resources(
        request.query,
        number_of_results=3
    )

    return {
        "query": request.query,
        "blocked": False,
        "results": results
    }

@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "Backend is running",
    }


@app.get("/")
async def serve_frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
