from agents import Agent, input_guardrail, function_tool, GuardrailFunctionOutput, InputGuardrailTripwireTriggered, ModelSettings, RunContextWrapper, Runner, set_default_openai_key
from common.db import get_conn
from common.models import Article, GuardrailOutput, TopicRequest
from dotenv import load_dotenv
from fastapi import FastAPI
import os
from pydantic import BaseModel

load_dotenv()
set_default_openai_key(os.environ["OPENAI_API_KEY"])
app = FastAPI()

"""
Defines the form taken by the output.
"""
class NewsSummary(BaseModel):
    topic: str
    key_events: str 
    themes: str
    overall_trend: str
    notable_sources: str

"""
FUNCTIONS
"""
@app.post("/analyze")
async def analyze_topic(request: TopicRequest):
    """
    Wrapper function to call search process and convert results to JSON.
    Args:
        topic: the topic to search.
    Returns:
        JSON-formatted result.
    """
    result = await run_analysis(request.topic)
    return result

def articles_to_text(articles: list[Article]) -> str:
    """
    Converts list of article into agent-parsible text.
    Args:
        articles: list of articles retrieved.
    Returns:
        list of articles in text form. 
    """
    output = []
    for article in articles:
        output.append(
            f"Title: {article.title}\n"
            f"Source: {article.source}\n"
            f"Published: {article.published_at}\n"
            f"Content: {article.content}\n"
        )
    if not output:
        return f"No articles found"
    return "\n---\n".join(output)


@function_tool
def get_articles_by_topic(topic: str) -> str:
    """
    Search SQL database for articles with provided topic.
    Args:
        topic: the topic to search.
    Returns:
        Article entries in text form.
    """
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT topic, title, source, url, published_at, content
            FROM articles
            WHERE topic = %s
                       ORDER BY published_at DESC
            LIMIT 20
            """, (topic,))
        rows = cursor.fetchall()
    articles = []
    for row in rows:
        articles.append(
            Article(
                topic=row[0] if row[0] is not None else "",
                title=row[1] if row[1] is not None else "",
                source=row[2] if row[2] is not None else "",
                url=row[3] if row[3] is not None else "",
                published_at= str(row[4]) if row[4] is not None else "",
                content=row[5] if row[5] is not None else ""
            )
        )
    conn.close()
    return articles_to_text(articles)

"""
Definition of response to inappropriate inputs
"""
@input_guardrail
async def offensive_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str,
) -> GuardrailFunctionOutput:
    response = await Runner.run(starting_agent=offensiveCheck, input = input)
    return GuardrailFunctionOutput(
        output_info = response.final_output,
        tripwire_triggered = response.final_output.is_triggered,
    )

"""
AGENTS
"""
"""
Agent to search for offensive content in inputs.
"""
offensiveCheck = Agent(
    name = "Offensive Checker",
    instructions = "Check the input for any offensive language." 
    "If it contains any, flag the input as inappropriate. If it does, return is_triggered=True. "
    "If it does not, return is_triggered=False. "
    "Always return a short reasoning string.",
    model = "gpt-4o-mini",
    output_type = GuardrailOutput
)

"""
Agent to summarize news of a given topic.
"""

summaryAgent = Agent(
    name = "Summary Agent",
    instructions = "You are analyzing a set of news articles about a topic."
    "Produce a concise news synthesis based only on the provided articles."
    "Identify the most important recurring events and themes across the set, not just one narrow subtopic."
    "If one subtopic appears frequently, include it, but do not let it dominate unless it is a major historical event."
    "Mention overall sentiment only if it is strongly evident from the article set."
    "If the articles cover multiple distinct concepts, reflect that in the summary."
    "Ignore sports and other minor, irrelevant topics unless there is nothing else of significance.",
    model = "gpt-4o-mini",
    output_type = NewsSummary
)

"""
Tool version of Summarize Agent
"""
summaryTool = summaryAgent.as_tool(
    tool_name = "summary_agent",
    tool_description = "You are analyzing a set of news articles about a topic."
    "Produce a concise news synthesis based only on the provided articles."
    "Identify the most important recurring events and themes across the set, not just one narrow subtopic."
    "If one subtopic appears frequently, include it, but do not let it dominate unless it is a major historical event."
    "Mention overall sentiment only if it is strongly evident from the article set."
    "If the articles cover multiple distinct concepts, reflect that in the summary."
    "Ignore sports and other minor, irrelevant topics unless there is nothing else of significance.",
)

"""
Lead agent to coordinate the summarizing process.
"""
agent = Agent(
    name = "Agent",
    input_guardrails= [offensive_guardrail],
    instructions = "Run get_articles_by_topic using the provided input as a parameter to gain a text-version of the articles stored in the SQL database."
    "Then, call summaryTool to create a summary of this information.",
    model = "gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required"),
    tools =[get_articles_by_topic, summaryTool]
)


async def run_analysis(topic:str):
    """
    Initiates Agent process.
    Args:
        topic: the topic to search.
    Returns:
        Final output of agent, or exceptions.
    """

    try:
        result = await Runner.run(
            starting_agent=agent,
            input=topic
        )
        return(result.final_output)
    except InputGuardrailTripwireTriggered:
        return("Blocked by Input Guardrail.")
    except Exception as e:
        return(f"error: {e}")
    
@app.get("/health")
def health():
    return {"status": "ok"}