from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
# from .storage.firestore import FirestoreClient
from .models.whisky import WhiskyInfo
from .models.tasting import TastingNote
from .sub_agents.image_analyst import image_analyst
from .sub_agents.tasting_note_analyst import tasting_note_analyst

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
    model="gemini-2.0-flash-lite",
    description="Whisky analysis and management agent",
    instruction="""
    あなたはウイスキーの分析と管理を統括するコーディネーターです。

    # 主な責務
    1. ユーザーの要求分類と適切なエージェントへの振り分け
    2. データの永続化と取得の管理

    # 利用可能なリソース
    ## サブエージェント
    - image_analyst: ウイスキー画像からのブランド・ボトル情報解析
    - tasting_note_analyst: テイスティングノートの生成・解析

    ## データ管理ツール
    - save_whisky_info: ウイスキー情報の保存
    - save_tasting_note: テイスティングノートの保存
    - get_whisky_history: 保存済みデータの履歴取得

    # 処理フロー
    1. ユーザー入力の分析
       - 要求内容を理解し、必要な処理を判断
       - 画像解析、テイスティング分析、履歴取得などを識別

    2. 適切なサブエージェントでの処理
       - 画像解析 → image_analyst
       - テイスティング関連 → tasting_note_analyst

    3. 解析結果の確認と操作選択
       - 結果をユーザーに提示
       - ユーザーは以下を選択可能:
         * 保存: Firestoreへの自動保存
         * 編集: 内容を修正して再確認

    4. データの永続化
       - 確定した情報をFirestoreに保存
       - 適切なツールを使用（save_whisky_info / save_tasting_note）

    5. 履歴管理
       - get_whisky_historyで過去のデータを取得・提示
    """,
    tools=[
        save_whisky_info,
        save_tasting_note,
        get_whisky_history,
        AgentTool(image_analyst),
        AgentTool(tasting_note_analyst),
    ],
)
