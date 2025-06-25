from google.adk.agents import Agent
from google.adk.tools import google_search
from .prompts import SEARCH_AGENT_INSTRUCTION

search_agent = Agent(
    model='gemini-2.5-flash',
    name='SearchAgent',
    description="Google検索に特化したエージェント",
    instruction=SEARCH_AGENT_INSTRUCTION,
    tools=[google_search,
           ],
)
