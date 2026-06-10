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
            SELECT id,title,description
            FROM projects
        """)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return {"projects": rows}

    except Exception as e:
        return {"error": str(e)}