from pydantic import BaseModel
from typing import List, Optional

class Project(BaseModel):
    title: str
    description: str

class Blog(BaseModel):
    title: str
    content: str
    author: str
    category: str = "General"
    tags: List[str] = []
    cover_image: str = ""

class Comment(BaseModel):
    name: str
    email: str
    content: str

class Contact(BaseModel):
    name: str
    email: str
    message: str
