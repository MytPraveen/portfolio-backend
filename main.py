from fastapi import FastAPI
import psycopg2

app = FastAPI()

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