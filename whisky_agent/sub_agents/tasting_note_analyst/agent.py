from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field, ValidationError
from ...storage.firestore import FirestoreClient # FirestoreClientをインポート
from .sub_agents.tasting_note_creator import tasting_note_creator
from .sub_agents.tasting_note_modifier import tasting_note_modifier
from .prompts import TASTING_NOTE_ANALYST_INSTRUCTION


def save_tasting_note_to_firestore(tool_context: ToolContext) -> dict:
    """テイスティングノートをFirestoreに保存する

    Args:
        tool_context: セッションステートにアクセスするためのコンテキスト

    Returns:
        保存結果の確認メッセージを含む辞書
    """
    # ユーザーIDをtool_contextまたはセッションステートから取得
    user_id = tool_context.user_id if hasattr(tool_context, 'user_id') else "default_user_id"

    print(f"--- Tool: save_tasting_note_to_firestore called for user {user_id} ---")

    tasting_note = tool_context.state.get("tasting_note", {})

    # Firestoreクライアントを使用してテイスティングノートを保存
    firestore_client = FirestoreClient()
    firestore_client.save_tasting_note(user_id, tasting_note)

    return {
        "action": "save_tasting_note_to_firestore",
        "message": f"Tasting note saved to Firestore for user {user_id}"
    }


tasting_note_analyst = Agent(
    name="tasting_note_analyst",
    model="gemini-2.5-flash-preview-05-20",
    description="ウイスキーのテイスティングノートを管理・分析するエージェント",
    instruction=TASTING_NOTE_ANALYST_INSTRUCTION,
    tools=[
        AgentTool(tasting_note_creator),
        AgentTool(tasting_note_modifier),
        save_tasting_note_to_firestore
    ])
