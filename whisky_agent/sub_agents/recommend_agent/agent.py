from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field, ValidationError
from ...storage.firestore import FirestoreClient # FirestoreClientをインポート
from .prompts import RECOMMEND_AGENT_INSTRUCTION
from ..search_agent.agent import search_agent
from google.adk.tools import agent_tool
from datetime import datetime
from zoneinfo import ZoneInfo

async def get_user_whisky_history_from_firestore(tool_context: ToolContext) -> dict:
    """テイスティングノートをFirestoreに保存する

    Args:
        tool_context: セッションステートにアクセスするためのコンテキスト

    Returns:
        保存結果の確認メッセージを含む辞書
    """
    user_id = tool_context.state.get("user_id", 'default_user_id')

    firestore_client = FirestoreClient()
    history = await firestore_client.get_whisky_history(user_id)

    return history


recommend_agent = Agent(
    name="recommend_agent",
    model="gemini-2.5-flash",
    description="ウイスキーのおすすめを提案したり、一般的な会話をするエージェント",
    instruction=RECOMMEND_AGENT_INSTRUCTION,
    tools=[get_user_whisky_history_from_firestore,
           agent_tool.AgentTool(search_agent),
           ]
    )
