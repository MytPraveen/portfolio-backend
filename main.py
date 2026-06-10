from pydantic import BaseModel

class Project(BaseModel):
    title: str
    description: str


@app.post("/projects")
def create_project(project: Project):

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