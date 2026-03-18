from common.db import get_conn
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()

RETRIEVAL_URL = "http://retrieval:8000/fetch"
ANALYSIS_URL = "http://analysis:8000/analyze"

def get_topics() -> list[str]:
    """
    Retrieves list of topics stored in DB for future display.
    Returns:
        List of topics.
    """
    with get_conn() as conn:
      with conn.cursor() as cursor:
         cursor.execute("""
                SELECT DISTINCT topic
                FROM articles
                WHERE topic IS NOT NULL AND topic != ''
                ORDER BY topic
                """)
         rows = cursor.fetchall()
      return [row[0] for row in rows]

@app.get("/", response_class=HTMLResponse)
def home():
    """
    Displays HTML.
    Returns:
        HTML display.
    """
    topics = get_topics()
    topic_items = "".join(f"<li>{topic}</li>" for topic in topics)

    return f"""
    <html>
      <body>
        <h1>News Agent</h1>
        <form action="/fetch" method="post">
          <input name="topic" placeholder="Topic">
          <button type="submit">Fetch</button>
        </form>
        <form action="/analyze" method="post">
          <input name="topic" placeholder="Topic">
          <button type="submit">Analyze</button>
        </form>
        <form action="/delete_topic" method="post">
          <input name="topic" placeholder="Topic">
          <button type="submit">Delete Topic</button>
        </form>
        <h2>Topics in Database</h2>
        <ul>
          {topic_items}
        </ul>
        <form action="/clear_database" method="post">
          <button type="submit">Clear Database</button>
          </form>
      </body>
    </html>
    """

@app.post("/analyze", response_class=HTMLResponse)
def analyze(topic: str = Form(...)) -> HTMLResponse:
    """
    Initiates analysis on a given topic.
    Args:
        topic: the topic to search.
    Returns:
        Topic analysis in text form.
    """
    if(topic == ''):
        return HTMLResponse(f"""
                        <html>
                          <body>
                            <pre>No topic provided</pre><a href='/'>Back</a>
                          </body>
                        </html>""")
    r = requests.post(ANALYSIS_URL, json={"topic": topic})
    return f"<pre>{r.text}</pre><a href='/'>Back</a>"

@app.post("/clear_database", response_class=HTMLResponse)
def clear_database() -> HTMLResponse:
    """
    Deletes all entries from SQL table.
    """
    with get_conn() as conn:
        with conn.cursor() as cursor:
          cursor.execute(
            """
            DELETE FROM articles 
            """
          ) 
        return HTMLResponse(f"""
                          <html>
                            <body>
                              <pre>Deleted all entries in database.</pre><a href='/'>Back</a>
                            </body>
                          </html>""")

@app.post("/delete_topic", response_class=HTMLResponse)
def delete_topic(topic: str = Form(...)) -> HTMLResponse:
    """
    Deletes all entries of given topic in SQL database.
    Args:
        topic: the topic to search.
    """
    topic = topic.lower()
    if(topic == ''):
        return HTMLResponse(f"""
                        <html>
                          <body>
                            <pre>No topic provided</pre><a href='/'>Back</a>
                          </body>
                        </html>""")
    with get_conn() as conn:
      with conn.cursor() as cursor:
        cursor.execute(
          """
          DELETE FROM articles 
          WHERE topic = %s
          """,
          (topic,)
        ) 
        deleted_count = cursor.rowcount
      conn.commit()
    return HTMLResponse(f"""
                        <html>
                          <body>
                            <pre>Deleted {deleted_count} articles for topic: {topic}</pre><a href='/'>Back</a>
                          </body>
                        </html>""")

@app.post("/fetch", response_class=HTMLResponse)
def fetch(topic: str = Form(...)) -> HTMLResponse:
    """
    Places articles of a given topic in SQL database.
    Args:
        topic: the topic to search.
    Returns:
        Result in HTML form.
    """
    if(topic == ''):
        return HTMLResponse(f"""
                        <html>
                          <body>
                            <pre>No topic provided</pre><a href='/'>Back</a>
                          </body>
                        </html>""")
    r = requests.post(RETRIEVAL_URL, json={"topic": topic})
    return f"<pre>{r.text}</pre><a href='/'>Back</a>"

@app.get("/health")
def health():
    return {"status": "ok"}