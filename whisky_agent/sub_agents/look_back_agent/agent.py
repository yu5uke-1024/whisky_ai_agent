from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext
from typing import List
from pydantic import BaseModel, Field, ValidationError
from collections import Counter
from ...storage.firestore import FirestoreClient # FirestoreClientをインポート
from .prompts import look_back_agent_INSTRUCTION


async def get_my_history(tool_context: ToolContext) -> dict:
    """ユーザーのウイスキー履歴をFirestoreから取得する

    Args:
        tool_context: セッションステートにアクセスするためのコンテキスト

    Returns:
        保存結果の確認メッセージを含む辞書
    """
    user_id = tool_context.state.get("user_id", 'default_user_id')

    firestore_client = FirestoreClient()
    history = await firestore_client.get_whisky_history(user_id)

    return history


look_back_agent = Agent(
    name="look_back_agent",
    model="gemini-2.5-flash",
    description="ユーザーからのリクエストに基づき、過去の履歴の提供、傾向の分析を行うエージェント",
    instruction=look_back_agent_INSTRUCTION,
    tools=[get_my_history]
    )
