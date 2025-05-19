from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="whisky_agent",
    model="gemini-2.0-flash-lite", #"gemini-1.5-flash",
    description="whisky ai agent",
    instruction="""
    あなたはウイスキーに詳しいバーテンダーです。\n
    ユーザーの質問に簡潔に答えて。必要に応じてgoogle_searchツールを使ってください。
    """,
    tools=[google_search],
)


# def get_current_time() -> dict:
#     """
#     Get the current time in the format YYYY-MM-DD HH:MM:SS
#     """
#     return {
#         "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#     }
