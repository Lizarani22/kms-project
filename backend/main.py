#main.py
# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from pathlib import Path
import csv

from auth import hash_password, verify_password, create_access_token

app = FastAPI(title="AI Knowledge Management System")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- PATHS ----------------
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "articles.csv"

# ---------------- IN-MEMORY DATA ----------------
users_db = {}
articles_db = []
stats = {"total_recommendations": 0}

# ---------------- MODELS ----------------
class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    role: str

class Article(BaseModel):
    id: str
    title: str
    content: str
    tags: str
    category: str
    usage: int = 0

class Ticket(BaseModel):
    content: str
    max_recommendations: int = 3

# ---------------- LOAD ARTICLES ----------------
def load_articles_from_csv():
    articles_db.clear()

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found at {CSV_PATH}")

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            articles_db.append(Article(
                id=row["article_id"],
                title=row["title"],
                content=row["content"],
                tags=row.get("tags", ""),
                category=row["category"],
                usage=0
            ))

    print(f"Loaded {len(articles_db)} articles")

load_articles_from_csv()

# ---------------- REGISTER ----------------
@app.post("/register")
def register(data: RegisterRequest):
    if data.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")

    users_db[data.username] = {
        "password": hash_password(data.password),
        "role": data.role
    }

    return {"message": "User registered successfully"}

# ---------------- LOGIN ----------------
@app.post("/login", response_model=LoginResponse)
def login(data: LoginRequest):
    user = users_db.get(data.username)

    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": data.username,
        "role": user["role"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"]
    }

# ---------------- ARTICLES ----------------
@app.get("/articles", response_model=List[Article])
def get_articles():
    return articles_db

# ---------------- TICKET ----------------
@app.post("/ticket")
def analyze_ticket(ticket: Ticket):
    stats["total_recommendations"] += 1

    ticket_text = ticket.content.lower()
    recommendations = []

    for article in articles_db:
        text = f"{article.title} {article.content} {article.tags}".lower()
        score = sum(1 for word in ticket_text.split() if word in text)

        if score > 0:
            recommendations.append({
                "id": article.id,
                "title": article.title,
                "content": article.content,
                "category": article.category,
                "score": score
            })

    return {"recommendations": recommendations}

# ---------------- STATS ----------------
@app.get("/stats")
def get_stats():
    return {
        "total_articles": len(articles_db),
        "total_recommendations": stats["total_recommendations"]
    }
