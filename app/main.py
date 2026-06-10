from fastapi import FastAPI
from app.database import get_connection
from app.models import Project, Blog, Contact

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Portfolio Backend Running"}


@app.get("/projects")
def get_projects():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id,title,description
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
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO projects(title,description)
            VALUES(%s,%s)
            """,
            (project.title, project.description)
        )

        conn.commit()

        cur.close()
        conn.close()

        return {"message": "Project created successfully"}

    except Exception as e:
        return {"error": str(e)}


@app.delete("/projects/{project_id}")
def delete_project(project_id: int):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM projects WHERE id=%s",
            (project_id,)
        )

        conn.commit()

        cur.close()
        conn.close()

        return {"message": "Project deleted successfully"}

    except Exception as e:
        return {"error": str(e)}

@app.get("/blogs")
def get_blogs():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id,title,content,author,created_at
            FROM blogs
            ORDER BY created_at DESC
        """)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        blogs = []

        for row in rows:
            blogs.append({
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "author": row[3],
                "created_at": str(row[4])
            })

        return {"blogs": blogs}

    except Exception as e:
        return {"error": str(e)}

@app.post("/blogs")
def create_blog(blog: Blog):

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO blogs(title,content,author)
            VALUES(%s,%s,%s)
            """,
            (blog.title, blog.content, blog.author)
        )

        conn.commit()

        cur.close()
        conn.close()

        return {"message": "Blog created successfully"}

    except Exception as e:
        return {"error": str(e)}


@app.delete("/blogs/{blog_id}")
def delete_blog(blog_id: int):

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM blogs WHERE id=%s",
            (blog_id,)
        )

        conn.commit()

        cur.close()
        conn.close()

        return {"message": "Blog deleted successfully"}

    except Exception as e:
        return {"error": str(e)}

@app.post("/contact")
def contact(contact: Contact):

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO contacts(name,email,message)
            VALUES(%s,%s,%s)
            """,
            (
                contact.name,
                contact.email,
                contact.message
            )
        )

        conn.commit()

        cur.close()
        conn.close()

        return {
            "message": "Message submitted successfully"
        }

    except Exception as e:
        return {"error": str(e)}

@app.get("/contacts")
def get_contacts():

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id,name,email,message,created_at
            FROM contacts
            ORDER BY created_at DESC
        """)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        contacts = []

        for row in rows:
            contacts.append({
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "message": row[3],
                "created_at": str(row[4])
            })

        return {"contacts": contacts}

    except Exception as e:
        return {"error": str(e)}
