from pydantic import BaseModel

class LibraryStats(BaseModel):
    library_name: str
    total_books: int
    total_copies: int