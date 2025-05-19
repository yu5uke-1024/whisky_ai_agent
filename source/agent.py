from google.adk.agents import Agent
from google.adk.tools import google_search
from pydantic import BaseModel, Field

class WhiskyInfo(BaseModel):
    name: str = Field(
        description="ウイスキーの名称。ブランド名と商品名を含めてください（例：'アードベッグ 10年'）。"
    )
    description: str = Field(
        description="ウイスキーの詳細な説明。香り、味わい、余韻、産地、蒸溜所情報、特徴などを含めてください。"
    )


root_agent = Agent(
    name="whisky_agent",
    model="gemini-2.0-flash-lite", #"gemini-1.5-flash",
    description="whisky ai agent",
    instruction="""
    あなたはウイスキーに詳しいバーテンダーです。\n
    ユーザーの質問におすすめのウイスキーをレクチャーしてください。
    重要: あなたの回答は、以下の構造に一致する有効なJSON形式である必要があります:
    {
        "name": "ここにウイスキーの名称を入力してください",
        "description": "ここにウイスキーの詳細説明を記載してください。香り、味わい、余韻、産地、蒸溜所情報、特徴などを含めてください。"
    }
    説明文や補足など、JSON以外のテキストは絶対に含めないでください。
    """,
    output_schema=WhiskyInfo,
    output_key="whisky",
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
