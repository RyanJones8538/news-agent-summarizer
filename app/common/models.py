from pydantic import BaseModel

"""
Defines the article as it will be stored in SQL.
"""
class Article(BaseModel):
    topic: str
    title: str
    source: str
    url: str
    published_at: str
    content: str

"""
Defines the output from when a guardrail is hit.
"""
class GuardrailOutput(BaseModel):
    is_triggered: bool
    reasoning: str

"""
Defines the form a request on a topic will take.
"""
class TopicRequest(BaseModel):
    topic: str