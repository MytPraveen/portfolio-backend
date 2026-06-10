from pydantic import BaseModel

class Project(BaseModel):
    title: str
    description: str

class Blog(BaseModel):
    title: str
    content: str
    author: str
