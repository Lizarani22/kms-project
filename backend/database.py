import sqlite3

conn = sqlite3.connect("data/kms.db", check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,
    title TEXT,
    content TEXT,
    category TEXT,
    usage INTEGER DEFAULT 0
)
""")

conn.commit()

