from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext
from ...storage.firestore import FirestoreClient
from .sub_agents.tasting_note_creator import tasting_note_creator
from .sub_agents.tasting_note_modifier import tasting_note_modifier
from ...models import WhiskyInfo
from ...models import create_whisky_id
from .prompts import tasting_note_agent_INSTRUCTION

def save_tasting_note(tool_context: ToolContext) -> dict:
    """テイスティングノートをFirestoreに保存する

    Args:
        tool_context: セッションステートにアクセスするためのコンテキスト

    Returns:
        保存結果の確認メッセージを含む辞書
    """
    user_id = tool_context.state.get("user_id", 'default_user_id')
    whisky_id = tool_context.state.get("whisky_id", 'default_whisky_id')

    print(f"--- Tool: save_tasting_note called for user {user_id} ---")

    tasting_note = tool_context.state.get("tasting_note", {})
    whisky_info = tool_context.state.get("whisky_info", {})

    # Firestoreクライアントを使用してテイスティングノートを保存
    firestore_client = FirestoreClient()
    firestore_client.save_whisky_info(user_id, whisky_id, tasting_note)
    firestore_client.save_whisky_info(user_id, whisky_id, whisky_info)

    return {
        "action": "save_tasting_note_to_firestore",
        "message": f"Tasting note saved to Firestore for user {user_id} and whisky {whisky_id}"
    }



whisky_info_creator = Agent(
    name="whisky_info_creator",
    model="gemini-2.5-flash",
    description="ウイスキーの情報を作成するエージェント",
    instruction="output_schemaに従ってウイスキーの情報を作成してください。",
    output_schema=WhiskyInfo,
    output_key="whisky_info",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    before_agent_callback=create_whisky_id
)


tasting_note_agent = Agent(
    name="tasting_note_agent",
    model="gemini-2.5-flash",
    description="ウイスキーのテイスティングノートを管理・分析するエージェント",
    instruction=tasting_note_agent_INSTRUCTION,
    tools=[
        AgentTool(tasting_note_creator),
        AgentTool(tasting_note_modifier),
        save_tasting_note,
        AgentTool(whisky_info_creator),
    ])
