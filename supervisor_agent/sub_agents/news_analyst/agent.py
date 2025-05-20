from google.adk.agents import Agent
from google.adk.tools import google_search

news_analyst = Agent(
    name="news_analyst",
    model="gemini-2.0-flash-lite",
    description="whisky News analyst agent",
    instruction="""
    あなたは、ウイスキーに関するニュースを分析し、要点をわかりやすく要約して提供するアシスタントです。

    ユーザーからウイスキー関連のニュースについて尋ねられた場合は、google_searchツールを使って該当するニュースを検索して回答してください。
    """,
    tools=[google_search],
)
