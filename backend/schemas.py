#schemas.py
from pydantic import BaseModel
from pydantic import BaseModel

class User(BaseModel):
    username: str
    password: str
    role: str  # "admin" or "user"

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

class Article(BaseModel):
    id: str   # 👈 THIS IS THE FIX
    title: str
    content: str
    category: str
    usage: int


class Ticket(BaseModel):
    content: str
    max_recommendations: int = 3


