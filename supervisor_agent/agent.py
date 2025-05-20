from google.adk.agents import Agent
from google.adk.tools import google_search
from pydantic import BaseModel, Field
from google.adk.tools.agent_tool import AgentTool
from .sub_agents.whisky_price_agent.agent import whisky_price_agent
from .sub_agents.news_analyst.agent import news_analyst
from .sub_agents.tasting_note_analyst.agent import tasting_note_analyst
from .tools.tools import get_current_time

# class WhiskyInfo(BaseModel):
#     name: str = Field(
#         description="ウイスキーの名称。ブランド名と商品名を含めてください（例：'アードベッグ 10年'）。"
#     )
#     description: str = Field(
#         description="ウイスキーの詳細な説明。香り、味わい、余韻、産地、蒸溜所情報、特徴などを含めてください。"
#     )

# root_agent = Agent(
#     name="whisky_agent",
#     model="gemini-2.0-flash-lite", #"gemini-1.5-flash",
#     description="whisky ai agent",
#     instruction="""
#     あなたはウイスキーに詳しいバーテンダーです。\n
#     ユーザーの質問に簡潔に答えてください。
#     以下はユーザーの情報です。
#     名前: {user_name}
#     好み: {user_preferences}
#     """,
# )

# root_agent = Agent(
#     name="whisky_agent",
#     model="gemini-2.0-flash-lite", #"gemini-1.5-flash",
#     description="whisky ai agent",
#     instruction="""
#     あなたはウイスキーに詳しいバーテンダーです。\n
#     ユーザーの質問におすすめのウイスキーをレクチャーしてください。
#     重要: あなたの回答は、以下の構造に一致する有効なJSON形式である必要があります:
#     {
#         "name": "ここにウイスキーの名称を入力してください",
#         "description": "ここにウイスキーの詳細説明を記載してください。香り、味わい、余韻、産地、蒸溜所情報、特徴などを含めてください。"
#     }
#     説明文や補足など、JSON以外のテキストは絶対に含めないでください。
#     """,
#     output_schema=WhiskyInfo,
#     output_key="whisky",
# )

root_agent = Agent(
    name="whisky_agent",
    model="gemini-2.0-flash-lite",
    description="whisky ai agent",
    instruction="""
    あなたはマネージャーエージェントとして、他のエージェントの業務を監督し、適切にタスクを割り当てる責任を持ちます。

    ユーザーからのリクエストに応じて、最も適切なエージェントにタスクを委任してください。あなたの判断で最適なエージェントを選びましょう。
    ただし、あなた自身で回答できるユーザーからの質問には、そのまま回答しても問題ないです。

    あなたがタスクを委任できるエージェントは以下の通りです：
    - whisky_price_agent（ウイスキーの価格に関する質問を担当）
    - tasting_note_analyst (ウイスキーのテイスティングに関する質問を担当)

    また、以下のツールにアクセスすることができます：
    - get_current_time（現在時刻の取得）
    - news_analyst (ウイスキーのニュースを取得)

    適切なエージェントまたはツールを選び、ユーザーのリクエストに対応してください。
    """,
    sub_agents=[whisky_price_agent],
    tools=[
      get_current_time,
      AgentTool(news_analyst),
      AgentTool(tasting_note_analyst),
      ],
)

# root_agent = Agent(
#     name="whisky_agent",
#     model="gemini-2.0-flash-lite", #"gemini-1.5-flash",
#     description="whisky ai agent",
#     instruction="""
#     あなたはウイスキーに詳しいバーテンダーです。\n
#     ユーザーの質問に簡潔に答えて。必要に応じてgoogle_searchツールを使ってください。
#     また、おすすめの
#     """,
#     tools=[google_search],
# )


# def get_current_time() -> dict:
#     """
#     Get the current time in the format YYYY-MM-DD HH:MM:SS
#     """
#     return {
#         "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#     }
