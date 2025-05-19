from google.adk.agents import Agent

root_agent = Agent(
    name="whisky_agent",
    model="gemini-1.5-flash",
    description="whisky ai agent",
    instruction="""
    あなたはウイスキーAIバーテンダー。\n
    ユーザーの質問に簡潔に答えて
    """,
)
