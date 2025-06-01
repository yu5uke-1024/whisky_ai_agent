from typing import Optional
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from .storage.firestore import FirestoreClient # FirestoreClientをインポート
from .sub_agents.image_analyst import image_analyst
from .sub_agents.tasting_note_analyst import tasting_note_analyst
from .prompts import INSTRUCTION
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.genai import types # For types.Content

# Firestoreクライアントのインスタンスを作成
firestore_client = FirestoreClient()

async def get_whisky_history() -> dict:
    """
    Firestoreからウイスキーの履歴を取得するツール。
    これまでに保存されたウイスキー情報をリストで返します。
    """
    try:
        # Firestoreからウイスキーの履歴を取得
        history = await firestore_client.get_whisky_history()
        return {
            "status": "success",
            "history": [whisky.model_dump() for whisky in history] # モデルを辞書形式に変換
        }
    except Exception as e:
        # エラーが発生した場合は、エラーメッセージを返す
        return {"status": "error", "error": str(e)}

def check_if_agent_should_run(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Logs entry and checks 'skip_llm_agent' in session state.
    If True, returns Content to skip the agent's execution.
    If False or not present, returns None to allow execution.
    """
    agent_name = callback_context.agent_name

    user_name = callback_context.state.get("user_name", 'ゆうすけ')
    callback_context.state["user_name"] = user_name

    user_id = callback_context.state.get("user_id", '123')
    callback_context.state["user_id"] = user_id

    return None



# ルートエージェントの定義
root_agent = Agent(
    name="whisky_agent",
    model="gemini-2.5-flash-preview-04-17",
    description="ウイスキー情報の統括コーディネーター。明確なエージェント委譲ルールに基づきタスクを調整します。",
    instruction=INSTRUCTION, # エージェントの指示プロンプト
    sub_agents=[
        image_analyst, # 画像解析サブエージェント
        tasting_note_analyst, # テイスティングノート分析サブエージェント
    ],
    tools=[
        get_whisky_history, # ウイスキー履歴取得ツール
    ],
    before_agent_callback=check_if_agent_should_run # Assign the callback
)
