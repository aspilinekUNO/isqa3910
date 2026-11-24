import csv
from pathlib import Path
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel
from search import search_resources, check_query_safety

from starlette.middleware.sessions import SessionMiddleware
from .auth.mock_provider import MockAuthProvider

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
PROJECT_ROOT = BASE_DIR.parent
auth_provider = MockAuthProvider()

app = FastAPI(
    title="Project Backend",
    version="0.1.0",
    description="Starter FastAPI backend for a Python + JavaScript web app.",
)

class SearchRequest(BaseModel):
    query: str

class MockLoginRequest(BaseModel):
    user_identifier: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv(
        "SESSION_SECRET",
        "development-only-secret-change-me"
    ),
    same_site="lax",
    https_only=False
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
def search_mps(
    search_request: SearchRequest,
    request: Request
):
    # Require the user to be logged in
    user = request.session.get("user")

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    # Check the query for student privacy/safety concerns
    allowed, reason = check_query_safety(
        search_request.query
    )

    if not allowed:
        return {
            "query": search_request.query,
            "blocked": True,
            "reason": reason,
            "results": []
        }

    # Search for relevant MPS resources
    results = search_resources(
        search_request.query,
        number_of_results=3
    )

    return {
        "query": search_request.query,
        "blocked": False,
        "results": results
    }

@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "Backend is running",
    }

@app.post("/api/auth/mock-login")
def mock_login(login: MockLoginRequest, request: Request):

    user = auth_provider.authenticate(
        login.user_identifier
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid development user."
        )

    request.session["user"] = {
        "user_id": user.user_id,
        "display_name": user.display_name,
        "email": user.email,
        "role": user.role,
        "school": user.school
    }

    return {
        "authenticated": True,
        "user": request.session["user"]
    }


@app.get("/api/auth/me")
def get_current_user(request: Request):

    user = request.session.get("user")

    if user is None:
        return {
            "authenticated": False,
            "user": None
        }

    return {
        "authenticated": True,
        "user": user
    }


@app.post("/api/auth/logout")
def logout(request: Request):

    request.session.clear()

    return {
        "authenticated": False
    }


@app.get("/")
async def serve_frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
