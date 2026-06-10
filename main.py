from fastapi import FastAPI
import psycopg2

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Portfolio Backend Running"}

@app.get("/projects")
def projects():

    conn = psycopg2.connect(
        host="localhost",
        database="portfolio_db",
        user="portfolio_user",
        password="YOUR_PASSWORD"
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT id,title,description
        FROM projects
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return {"projects": rows}