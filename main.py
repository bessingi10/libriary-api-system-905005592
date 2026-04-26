from pydantic import BaseModel
from fastapi import FastAPI
from typing import Dict, List
from datetime import datetime, timedelta
import asyncio

class BorrowRequest(BaseModel):
    user_id: int
    book_id: int


class ReturnRequest(BaseModel):
    user_id: int
    book_id: int

app = FastAPI()

# Fake database
books: Dict[int, Dict] = {
    1: {"title": "Things Fall Apart", "author": "Chinua Achebe", "category": "Fiction", "available": True},
    2: {"title": "Python Basics", "author": "John Doe", "category": "Education", "available": True},
}

borrowed_books: Dict[int, Dict] = {}

# ✅ HOME ROUTE
@app.get("/")
async def home() -> Dict[str, str]:
    return {"message": "Library API is running"}

# ✅ GET ALL BOOKS
@app.get("/books")
async def get_books() -> List[Dict]:
    return list(books.values())

# ✅ SEARCH BOOKS
@app.get("/books/search")
async def search_books(title: str = "", author: str = "", category: str = "") -> List[Dict]:
    results = []
    for book in books.values():
        if (title.lower() in book["title"].lower() and
            author.lower() in book["author"].lower() and
            category.lower() in book["category"].lower()):
            results.append(book)
    return results

# ✅ BORROW BOOK (POST)
@app.post("/borrow")
async def borrow_book(data: BorrowRequest) -> Dict:
    await asyncio.sleep(1)

    book_id = data.book_id
    user_id = data.user_id

    if book_id not in books:
        return {"error": "Book not found"}

    if not books[book_id]["available"]:
        return {"error": "Book already borrowed"}

    books[book_id]["available"] = False
    due_date = datetime.now() + timedelta(days=7)

    borrowed_books[book_id] = {
        "user_id": user_id ,
        "due_date": due_date
    }

    return {
        "message": "Book borrowed successfully",
        "due_date": due_date.strftime("%Y-%m-%d")
    }
@app.post("/return")
async def return_book(data: ReturnRequest) -> Dict:
    await asyncio.sleep(1)

    book_id = data.book_id
    user_id = data.user_id

    if book_id not in borrowed_books:
        return {"error": "This book was not borrowed"}

    record = borrowed_books.pop(book_id)
    books[book_id]["available"] = True

    overdue_days = (datetime.now() - record["due_date"]).days
    fine = max(0, overdue_days * 50)

    return {
        "message": "Book returned successfully",
        "fine": fine
    }

# ✅ CHECK OVERDUE
@app.get("/overdue")
async def check_overdue(user_id: int) -> List[Dict]:
    results = []
    for book_id, record in borrowed_books.items():
        if record["user_id"] == user_id:
            overdue_days = (datetime.now() - record["due_date"]).days
            if overdue_days > 0:
                results.append({
                    "book_id": book_id,
                    "days_overdue": overdue_days,
                    "fine": overdue_days * 50
                })
    return results