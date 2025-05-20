from google.adk.agents import Agent
from google.adk.tools import google_search

news_analyst = Agent(
    name="news_analyst",
    model="gemini-2.0-flash-lite",
    description="whisky News analyst agent",
    instruction="""
    あなたは、ウイスキーに関するニュースを分析し、要点をわかりやすく要約できるアシスタントです。

    ユーザーからウイスキー関連のニュースについて尋ねられた場合は、google_searchツールを使って該当するニュースを検索してください。

    また、ユーザーが「最近のニュース」や「今日のニュース」といった相対的な時間表現で尋ねた場合は、
    get_current_timeツールを使って現在の時刻を取得し、検索クエリに活用してください。
    """,
    tools=[google_search],
)
