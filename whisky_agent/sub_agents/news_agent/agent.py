from google.adk.agents import Agent
from .prompts import NEWS_AGENT_INSTRUCTION
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.langchain_tool import LangchainTool
from langchain_community.tools import TavilySearchResults

from datetime import datetime
from zoneinfo import ZoneInfo

def get_tokyo_time() -> str:
    """
    東京の現在時刻をJSTで取得して、文字列として返します。

    Returns:
        str: 東京の現在時刻を示すフォーマットされた文字列。
    """
    # 東京のタイムゾーンを指定
    tokyo_tz = ZoneInfo("Asia/Tokyo")

    # 指定したタイムゾーンで現在時刻を取得
    now = datetime.now(tokyo_tz)

    # 結果を分かりやすい文字列にフォーマット
    report = f'東京の現在時刻は {now.strftime("%Y-%m-%d %H:%M:%S %Z")} です。'

    return {"status": "success", "report": report}



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
    ユーザーの質問に対して、検索結果と参照先のリンクを必ず出力してください。
    """,
    #tools=[google_search]
    tools=[adk_tavily_tool]
    )

news_agent = Agent(
    model='gemini-2.5-flash',
    name='news_agent',
    description="ウイスキーのニュース検索に特化したエージェント",
    instruction=NEWS_AGENT_INSTRUCTION,
    tools=[AgentTool(search_agent), get_tokyo_time]
    )
