from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field, ValidationError
from collections import Counter
from ...storage.firestore import FirestoreClient # FirestoreClientをインポート
from .prompts import RECORD_AGENT_INSTRUCTION

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

async def analyze_whisky_by_country(tool_context: ToolContext) -> dict:
    """ユーザーのウイスキー履歴を国別で集計する

    Args:
        tool_context: セッションステートにアクセスするためのコンテキスト

    Returns:
        国別集計結果を含む辞書
    """
    user_id = tool_context.state.get("user_id", 'default_user_id')

    firestore_client = FirestoreClient()
    history = await firestore_client.get_whisky_history(user_id)
    
    if not history or not isinstance(history, list):
        return {"error": "履歴データが見つかりません"}
    
    country_counts = Counter()
    for whisky in history:
        if isinstance(whisky, dict) and "country" in whisky:
            country_counts[whisky["country"]] += 1
    
    result = {
        "total_whiskies": len(history),
        "countries": dict(country_counts),
        "unique_countries": len(country_counts)
    }
    
    return result

record_agent = Agent(
    name="record_agent",
    model="gemini-2.5-flash",
    description="ユーザーからのリクエストに基づき、過去の履歴の提供、傾向の分析を行うエージェント",
    instruction=RECORD_AGENT_INSTRUCTION,
    tools=[get_my_history,
           analyze_whisky_by_country
           ]
    )
