from google.adk.agents import Agent
from .prompts import NEWS_AGENT_INSTRUCTION
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

search_agent = Agent(
    model='gemini-2.5-flash',
    name='search_agent',
    description="google検索をするエージェント",
    instruction="google検索をした結果を返す",
    tools=[google_search]
    )


news_agent = Agent(
    model='gemini-2.5-flash',
    name='news_agent',
    description="ウイスキーのニュース検索に特化したエージェント",
    instruction=NEWS_AGENT_INSTRUCTION,
    tools=[AgentTool(search_agent)]
    )
