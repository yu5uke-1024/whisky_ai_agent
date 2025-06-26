from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field, ValidationError
from ...storage.firestore import FirestoreClient # FirestoreClientをインポート
from .prompts import RECOMMEND_AGENT_INSTRUCTION

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

async def get_other_history(tool_context: ToolContext) -> dict:
    """他のユーザーのウイスキー履歴をFirestoreから取得する

    Args:
        tool_context: セッションステートにアクセスするためのコンテキスト

    Returns:
        保存結果の確認メッセージを含む辞書
    """
    user_id = tool_context.state.get("user_id", 'default_user_id')
    firestore_client = FirestoreClient()
    history = await firestore_client.get_whisky_history(exclude_user_id=user_id)  # 現在のユーザーIDを除外

    return history


recommend_agent = Agent(
    name="recommend_agent",
    model="gemini-2.5-flash",
    description="ユーザーの好みやウイスキー履歴を分析し、パーソナライズされたウイスキー推薦や一般的な日常会話やウイスキーの知識を提供するエージェント",
    instruction=RECOMMEND_AGENT_INSTRUCTION,
    tools=[get_my_history,
           get_other_history,
           ]
    )
