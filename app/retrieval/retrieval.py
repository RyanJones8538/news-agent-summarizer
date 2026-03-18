from agents import Agent, input_guardrail, function_tool, GuardrailFunctionOutput, InputGuardrailTripwireTriggered, RunContextWrapper, Runner, set_default_openai_key
from common.db import get_conn
from common.models import Article, GuardrailOutput, TopicRequest
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import feedparser
import os
import psycopg
from urllib.parse import quote_plus

load_dotenv()
set_default_openai_key(os.environ["OPENAI_API_KEY"])
app = FastAPI()

"""
FUNCTIONS
"""

@function_tool
def fetch_and_store_articles(topic: str) -> str:
    """
    Fetches a list of articles, and stores each article
    Args:
        topic: the topic to search.
    Returns:
        explanation of results
    """
    articles = fetch_articles(topic)
    with get_conn() as conn:
        for article in articles:
            save_article(article, conn)
        conn.commit()

    return f"Stored {len(articles)} articles about {topic}"

def fetch_articles(topic: str) -> list[Article]:
    """
    Fetch news articles on a given topic.
    Args:
        topic: the topic to search.
    Returns:
        list of articles 
    """
    encoded_topic = quote_plus(topic)
    url = f"https://news.google.com/rss/search?q={encoded_topic}"

    feed = feedparser.parse(url)

    articles = []

    for entry in feed.entries:
        articles.append(
            Article(
                topic=topic,
                title=getattr(entry, "title", ""),
                source=entry.source.title if hasattr(entry, "source") and hasattr(entry.source, "title") else "unknown",
                url=getattr(entry, "link", ""),
                published_at=getattr(entry, "published", ""),
                content=getattr(entry, "summary", "")
            )
        )

    return articles

@app.post("/fetch")
async def fetch_topic(request: TopicRequest):
    """
    Starts process of searching for articles.
    Args:
        topic: the topic to search.
    Returns:
        explanation of results 
    """
    topic = request.topic.lower()
    result = await run_retrieval(topic)
    return HTMLResponse(f"""
                        <html>
                          <body>
                            <pre>{result}</pre><a href='/'>Back</a>
                          </body>
                        </html>""")

"""
Definition of response to inappropriate inputs
"""
@input_guardrail
async def offensive_guardrail(
    ctx: RunContextWrapper[None],
    retrievalAgent: Agent,
    input: str,
) -> GuardrailFunctionOutput:
    response = await Runner.run(starting_agent=offensiveCheck, input = input)
    return GuardrailFunctionOutput(
        output_info = response.final_output,
        tripwire_triggered = response.final_output.is_triggered,
    )

def save_article(article: Article, conn: psycopg.Connection) -> None:
    """
    Fetch news articles on a given topic.
    Args:
        article: an individual article
        conn: the connection to the SQL database
    """
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO articles (topic, title, source, url, published_at, content)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON CONFLICT (url) DO NOTHING
            """, (
                article.topic,
                article.title,
                article.source,
                article.url,
                article.published_at,
                article.content
                )
            )

async def run_retrieval(topic: str) -> str:
    """
    Initiates Agent and handles exceptions.
    """
    try:
        result = await Runner.run(
            starting_agent=retrievalAgent,
            input=topic
        )
        return (result.final_output)
    except InputGuardrailTripwireTriggered:
        return("Blocked by Input Guardrail.")
    except Exception as e:
        return(f"error: {e}")


"""
AGENTS
"""
"""
Tool version of agent to check for inappropriate inputs.
"""
offensiveCheck = Agent(
    name = "Offensive Checker",
    instructions = "Check the input for any offensive language." \
    "If it contains any, flag the input as inappropriate. If it does, return is_triggered=True. "
    "If it does not, return is_triggered=False. "
    "Always return a short reasoning string.",
    model = "gpt-4o-mini",
    output_type = GuardrailOutput
)

"""
Agent which checks for inappropriate inputs and begins search for articles.
"""
retrievalAgent = Agent(
    name = "Agent",
    input_guardrails= [offensive_guardrail],
    instructions = "Run fetch_and_store_articles to retrieve the relevant feed from Google RSS and allow it to place them in the SQL database. If you encounter an error, tell me about the error in specific terms.",
    model = "gpt-4o-mini",
    tools =[fetch_and_store_articles]
)

@app.get("/health")
def health():
    return {"status": "ok"}