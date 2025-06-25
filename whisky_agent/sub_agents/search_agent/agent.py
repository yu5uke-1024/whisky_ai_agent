from google.adk.agents import Agent
from google.adk.tools import google_search

search_agent = Agent(
    model='gemini-2.5-flash',
    name='SearchAgent',
    description="google検索に特化したエージェント",
    instruction="""google_searchツールでgoogle検索を実施""",
    tools=[google_search,
           ],
)
