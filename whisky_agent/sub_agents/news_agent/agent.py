from google.adk.agents import Agent
from .prompts import NEWS_AGENT_INSTRUCTION
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.langchain_tool import LangchainTool
from langchain_community.tools import TavilySearchResults

tavily_tool_instance = TavilySearchResults(
    max_results=3,
    search_topic="news",
    search_depth="basic",
    include_answer=False,
    include_raw_content=False,
    include_images=False,
    include_domains = ["https://prtimes.jp/"]
)

# Wrap it with LangchainTool for ADK
adk_tavily_tool = LangchainTool(tool=tavily_tool_instance)


search_agent = Agent(
    model='gemini-2.5-flash',
    name='search_agent',
    description="web検索をするエージェント",
    instruction="""
    あなたはweb検索エージェントです。
    ユーザーの質問に対して、検索結果の要約と参照先のリンクを必ず出力してください。
    """,
    #tools=[google_search]
    tools=[adk_tavily_tool]
    )

news_agent = Agent(
    model='gemini-2.5-flash',
    name='news_agent',
    description="ウイスキーのニュース検索に特化したエージェント",
    instruction=NEWS_AGENT_INSTRUCTION,
    tools=[AgentTool(search_agent)]
    )
