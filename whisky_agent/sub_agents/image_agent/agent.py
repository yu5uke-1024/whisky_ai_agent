from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from typing import Dict, Any
from pydantic import BaseModel, Field
from .sub_agents.image_modifier import image_modifier
from .sub_agents.whisky_label_processor import whisky_label_processor
from .prompts import image_agent_INSTRUCTION
from whisky_agent.storage.firestore import FirestoreClient
from google.adk.tools.tool_context import ToolContext

def save_whisky_info_to_firestore(tool_context: ToolContext) -> dict:
    """ウイスキー情報をFirestoreに保存する

    Args:
        tool_context: セッションステートにアクセスするためのコンテキスト

    Returns:
        保存結果の確認メッセージを含む辞書
    """
    user_id = tool_context.state.get("user_id", 'default_user_id')
    whisky_id = tool_context.state.get("whisky_id", 'default_whisky_id')

    print(f"--- Tool: save_tasting_note_to_firestore called for user {user_id} ---")

    whisky_info = tool_context.state.get("whisky_info", {})

    # Firestoreクライアントを使用してテイスティングノートを保存
    firestore_client = FirestoreClient()
    firestore_client.save_whisky_info(user_id, whisky_id, whisky_info)

    return {
        "action": "save_whisky_info_to_firestore",
        "message": f"Whisky info saved to Firestore for user {user_id} and whisky {whisky_id}"
    }


image_agent = Agent(
    name="image_agent",
    model="gemini-2.5-flash",
    description="ウイスキーのラベル画像から情報を抽出する専門家",
    instruction=image_agent_INSTRUCTION,
    sub_agents=[whisky_label_processor],
    tools=[
        AgentTool(image_modifier),
        save_whisky_info_to_firestore
        ]
)
