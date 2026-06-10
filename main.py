from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2

app = FastAPI()

class Project(BaseModel):
    title: str
    description: str

@app.get("/")
def home():
    return {"message": "Portfolio Backend Running"}

@app.get("/projects")
def projects():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="portfolio_db",
            user="portfolio_user",
            password="Paul@1970"
        )

        cur = conn.cursor()

        cur.execute("""
            SELECT id, title, description
            FROM projects
        """)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        projects = []

        for row in rows:
            projects.append({
                "id": row[0],
                "title": row[1],
                "description": row[2]
            })

        return {"projects": projects}

    except Exception as e:
        return {"error": str(e)}

@app.post("/projects")
def create_project(project: Project):
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="portfolio_db",
            user="portfolio_user",
            password="Paul@1970"
        )

        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO projects (title, description)
            VALUES (%s, %s)
            """,
            (project.title, project.description)
        )

        conn.commit()

        cur.close()
        conn.close()

        return {"message": "Project created successfully"}

    except Exception as e:
        return {"error": str(e)}