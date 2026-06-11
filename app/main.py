from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import get_connection
from app.models import Project, Blog, Contact, Comment
import os, shutil, uuid
from pathlib import Path

app = FastAPI(title="Praveen Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


# ── DB INIT ──────────────────────────────────────────────────────────────────
@app.on_event("startup")
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS blogs (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            tags TEXT DEFAULT '',
            cover_image TEXT DEFAULT '',
            read_time INT DEFAULT 5,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS blog_images (
            id SERIAL PRIMARY KEY,
            blog_id INT REFERENCES blogs(id) ON DELETE CASCADE,
            filename TEXT NOT NULL,
            caption TEXT DEFAULT '',
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id SERIAL PRIMARY KEY,
            blog_id INT REFERENCES blogs(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


# ── HEALTH ────────────────────────────────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "Portfolio Backend Running", "status": "healthy"}

@app.get("/health")
def health():
    return {"status": "ok"}


# ── PROJECTS ──────────────────────────────────────────────────────────────────
@app.get("/projects")
def get_projects():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id,title,description,created_at FROM projects ORDER BY created_at DESC")
        rows = cur.fetchall()
        cur.close(); conn.close()
        return {"projects": [{"id":r[0],"title":r[1],"description":r[2],"created_at":str(r[3])} for r in rows]}
    except Exception as e:
        return {"error": str(e)}

@app.post("/projects")
def create_project(project: Project):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO projects(title,description) VALUES(%s,%s)", (project.title, project.description))
        conn.commit(); cur.close(); conn.close()
        return {"message": "Project created successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/projects/{project_id}")
def delete_project(project_id: int):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM projects WHERE id=%s", (project_id,))
        conn.commit(); cur.close(); conn.close()
        return {"message": "Project deleted successfully"}
    except Exception as e:
        return {"error": str(e)}


# ── BLOGS ─────────────────────────────────────────────────────────────────────
@app.get("/blogs")
def get_blogs():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id,title,content,author,category,tags,cover_image,read_time,created_at,updated_at
            FROM blogs ORDER BY created_at DESC
        """)
        rows = cur.fetchall()
        cur.close(); conn.close()
        return {"blogs": [{
            "id": r[0], "title": r[1], "content": r[2], "author": r[3],
            "category": r[4], "tags": r[5].split(",") if r[5] else [],
            "cover_image": r[6], "read_time": r[7],
            "created_at": str(r[8]), "updated_at": str(r[9])
        } for r in rows]}
    except Exception as e:
        return {"error": str(e)}

@app.get("/blogs/{blog_id}")
def get_blog(blog_id: int):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id,title,content,author,category,tags,cover_image,read_time,created_at,updated_at
            FROM blogs WHERE id=%s
        """, (blog_id,))
        r = cur.fetchone()
        if not r:
            raise HTTPException(status_code=404, detail="Blog not found")

        # get images
        cur.execute("SELECT id,filename,caption FROM blog_images WHERE blog_id=%s ORDER BY id", (blog_id,))
        images = [{"id": i[0], "filename": i[1], "caption": i[2], "url": f"/uploads/{i[1]}"} for i in cur.fetchall()]

        # get comments
        cur.execute("SELECT id,name,email,content,created_at FROM comments WHERE blog_id=%s ORDER BY created_at DESC", (blog_id,))
        comments = [{"id":c[0],"name":c[1],"email":c[2],"content":c[3],"created_at":str(c[4])} for c in cur.fetchall()]

        cur.close(); conn.close()
        return {
            "id": r[0], "title": r[1], "content": r[2], "author": r[3],
            "category": r[4], "tags": r[5].split(",") if r[5] else [],
            "cover_image": r[6], "read_time": r[7],
            "created_at": str(r[8]), "updated_at": str(r[9]),
            "images": images, "comments": comments
        }
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e)}

@app.post("/blogs")
def create_blog(blog: Blog):
    try:
        conn = get_connection()
        cur = conn.cursor()
        tags_str = ",".join(blog.tags) if blog.tags else ""
        # rough read time: 200 words/min
        read_time = max(1, len(blog.content.split()) // 200)
        cur.execute("""
            INSERT INTO blogs(title,content,author,category,tags,cover_image,read_time)
            VALUES(%s,%s,%s,%s,%s,%s,%s) RETURNING id
        """, (blog.title, blog.content, blog.author, blog.category, tags_str, blog.cover_image, read_time))
        blog_id = cur.fetchone()[0]
        conn.commit(); cur.close(); conn.close()
        return {"message": "Blog created successfully", "id": blog_id}
    except Exception as e:
        return {"error": str(e)}

@app.put("/blogs/{blog_id}")
def update_blog(blog_id: int, blog: Blog):
    try:
        conn = get_connection()
        cur = conn.cursor()
        tags_str = ",".join(blog.tags) if blog.tags else ""
        read_time = max(1, len(blog.content.split()) // 200)
        cur.execute("""
            UPDATE blogs SET title=%s,content=%s,author=%s,category=%s,
            tags=%s,cover_image=%s,read_time=%s,updated_at=NOW()
            WHERE id=%s
        """, (blog.title, blog.content, blog.author, blog.category, tags_str, blog.cover_image, read_time, blog_id))
        conn.commit(); cur.close(); conn.close()
        return {"message": "Blog updated successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/blogs/{blog_id}")
def delete_blog(blog_id: int):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM blogs WHERE id=%s", (blog_id,))
        conn.commit(); cur.close(); conn.close()
        return {"message": "Blog deleted successfully"}
    except Exception as e:
        return {"error": str(e)}


# ── BLOG IMAGE UPLOAD ─────────────────────────────────────────────────────────
@app.post("/blogs/{blog_id}/images")
async def upload_blog_image(
    blog_id: int,
    file: UploadFile = File(...),
    caption: str = Form(default="")
):
    try:
        # validate type
        if file.content_type not in ["image/jpeg","image/png","image/gif","image/webp"]:
            raise HTTPException(status_code=400, detail="Only image files allowed")

        ext = file.filename.rsplit(".", 1)[-1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        dest = UPLOAD_DIR / filename

        with dest.open("wb") as buf:
            shutil.copyfileobj(file.file, buf)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO blog_images(blog_id,filename,caption) VALUES(%s,%s,%s) RETURNING id",
            (blog_id, filename, caption)
        )
        img_id = cur.fetchone()[0]
        conn.commit(); cur.close(); conn.close()

        return {"id": img_id, "filename": filename, "url": f"/uploads/{filename}", "caption": caption}
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e)}

@app.delete("/blogs/{blog_id}/images/{image_id}")
def delete_blog_image(blog_id: int, image_id: int):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT filename FROM blog_images WHERE id=%s AND blog_id=%s", (image_id, blog_id))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Image not found")
        filepath = UPLOAD_DIR / row[0]
        if filepath.exists():
            filepath.unlink()
        cur.execute("DELETE FROM blog_images WHERE id=%s", (image_id,))
        conn.commit(); cur.close(); conn.close()
        return {"message": "Image deleted"}
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e)}


# ── COMMENTS ──────────────────────────────────────────────────────────────────
@app.get("/blogs/{blog_id}/comments")
def get_comments(blog_id: int):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id,name,email,content,created_at FROM comments WHERE blog_id=%s ORDER BY created_at DESC",
            (blog_id,)
        )
        rows = cur.fetchall()
        cur.close(); conn.close()
        return {"comments": [{"id":r[0],"name":r[1],"email":r[2],"content":r[3],"created_at":str(r[4])} for r in rows]}
    except Exception as e:
        return {"error": str(e)}

@app.post("/blogs/{blog_id}/comments")
def add_comment(blog_id: int, comment: Comment):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO comments(blog_id,name,email,content) VALUES(%s,%s,%s,%s) RETURNING id,created_at",
            (blog_id, comment.name, comment.email, comment.content)
        )
        row = cur.fetchone()
        conn.commit(); cur.close(); conn.close()
        return {"id": row[0], "message": "Comment added", "created_at": str(row[1])}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/comments/{comment_id}")
def delete_comment(comment_id: int):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM comments WHERE id=%s", (comment_id,))
        conn.commit(); cur.close(); conn.close()
        return {"message": "Comment deleted"}
    except Exception as e:
        return {"error": str(e)}


# ── CONTACT ───────────────────────────────────────────────────────────────────
@app.post("/contact")
def contact(contact: Contact):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO contacts(name,email,message) VALUES(%s,%s,%s)",
            (contact.name, contact.email, contact.message)
        )
        conn.commit(); cur.close(); conn.close()
        return {"message": "Message submitted successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/contacts")
def get_contacts():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id,name,email,message,created_at FROM contacts ORDER BY created_at DESC")
        rows = cur.fetchall()
        cur.close(); conn.close()
        return {"contacts": [{"id":r[0],"name":r[1],"email":r[2],"message":r[3],"created_at":str(r[4])} for r in rows]}
    except Exception as e:
        return {"error": str(e)}
