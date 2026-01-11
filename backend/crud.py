# backend/crud.py
from .database import conn
from backend import schemas
import pandas as pd
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

# Load initial data
def load_articles():
    df = pd.read_csv("data/articles.csv")

    for _, row in df.iterrows():
        conn.execute(
            """
            INSERT OR IGNORE INTO articles
            (id, title, content, category, usage)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                row.article_id,
                row.title,
                row.content,
                row.category,
                0
            )
        )
    conn.commit()


def get_all_articles():
    cursor = conn.execute("SELECT * FROM articles")
    rows = cursor.fetchall()
    return [
        {
            "id": r[0],
            "title": r[1],
            "content": r[2],
            "category": r[3],
            "usage": r[4]
        }
        for r in rows
    ]


def get_recommendations(ticket: schemas.Ticket):
    cursor = conn.execute("SELECT * FROM articles")
    articles = cursor.fetchall()

    ticket_emb = model.encode(ticket.content, convert_to_tensor=True)
    scored = []

    for a in articles:
        # combine title + content for better semantic match
        article_text = f"{a[1]} {a[2]}"
        art_emb = model.encode(article_text, convert_to_tensor=True)

        score = util.cos_sim(ticket_emb, art_emb).item()

        if score >= 0.35:
            scored.append({
                "id": a[0],
                "title": a[1],
                "content": a[2],
                "category": a[3],
                "score": score
            })

    # sort by similarity
    scored.sort(key=lambda x: x["score"], reverse=True)

    # limit results
    results = scored[:ticket.max_recommendations]

    # update usage ONLY for returned articles
    for r in results:
        conn.execute(
            "UPDATE articles SET usage = usage + 1 WHERE id = ?",
            (r["id"],)
        )

    conn.commit()
    return results


def get_stats():
    cursor = conn.execute("SELECT COUNT(*), SUM(usage) FROM articles")
    total_articles, total_usage = cursor.fetchone()

    return {
        "total_articles": total_articles,
        "total_recommendations": total_usage or 0
    }
