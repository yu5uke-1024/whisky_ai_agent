from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
# from .storage.firestore import FirestoreClient
from .models.whisky import WhiskyInfo
from .models.tasting import TastingNote
from .sub_agents.image_analyst import image_analyst
from .sub_agents.tasting_note_analyst import tasting_note_analyst
from .prompts import INSTRUCTION

# Firestoreクライアントのインスタンスを作成
# firestore_client = FirestoreClient()

async def save_whisky_info(whisky_info: dict) -> dict:
    """ウイスキー情報を保存するツール"""
    try:
        whisky = WhiskyInfo(
            name=whisky_info.get('brand', '不明'),
            image_analysis=whisky_info
        )
        # whisky_id = await firestore_client.save_whisky(whisky)
        whisky_id = "123"
        return {
            "status": "success",
            "whisky_id": whisky_id,
            "message": "ウイスキー情報を保存しました"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def save_tasting_note(note_info: dict) -> dict:
    """テイスティングノートを保存するツール"""
    try:
        note = TastingNote(
            whisky_id=note_info['whisky_id'],
            nose=note_info.get('nose', []),
            palate=note_info.get('palate', []),
            finish=note_info.get('finish', []),
            rating=note_info.get('rating'),
            memo=note_info.get('memo')
        )
        # note_id = await firestore_client.save_tasting_note(note)
        note_id = "123"
        return {
            "status": "success",
            "note_id": note_id,
            "message": "テイスティングノートを保存しました"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def get_whisky_history() -> dict:
    """ウイスキーの履歴を取得するツール"""
    try:
        # history = await firestore_client.get_whisky_history()
        history = []
        return {
            "status": "success",
            "history": [whisky.model_dump() for whisky in history]
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

root_agent = Agent(
    name="whisky_agent",
    model="gemini-2.5-flash-preview-05-20",
    description="Whisky analysis coordinator with clear agent delegation rules",
    instruction=INSTRUCTION,
    sub_agents=[
        image_analyst,
    ],
    tools=[
        save_whisky_info,
        save_tasting_note,
        get_whisky_history,
        AgentTool(tasting_note_analyst),
        # AgentTool(image_analyst),
    ],
)
