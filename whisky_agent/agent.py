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
    model="gemini-2.5-flash-preview-05-20",
    description="Whisky analysis coordinator with clear agent delegation rules",
    instruction="""
    あなたはウイスキー情報の統括コーディネーターです。
    明確な役割分担に基づいて、タスクを適切に振り分けてください。

    # 厳格な役割分担
    ## サブエージェントが必ず担当するタスク（必ずサブエージェントに転送）
    1. image_analyst
       - 全ての画像解析タスク
       - 入力：ウイスキーの画像
       - 処理：ブランド、蒸溜所、年数、度数などの情報抽出

    2. tasting_note_analyst
       - 全てのテイスティングノート生成タスク
       - 入力：ウイスキー名や特徴
       - 処理：香り、味わい、余韻、評価の分析と生成

    ## あなたが直接担当するタスク（サブエージェントに転送しない）
    1. 編集作業
       - 解析済み画像情報の修正
       - 生成済みテイスティングノートの編集
       - 保存済みデータの更新

    2. 一般的な質問への回答
       - ウイスキーの基礎知識
       - 製法や特徴の説明
       - 用語の解説

    3. データ管理
       - save_whisky_info: 情報の保存
       - save_tasting_note: ノートの保存
       - get_whisky_history: 履歴の取得

    # 処理判断フロー
    1. 入力タイプの判別
       - 画像添付あり → 必ずimage_analystへ
       - テイスティングノート作成要求 → 必ずtasting_note_analystへ
       - 既存データの編集要求 → あなたが直接処理
       - 一般的な質問 → あなたが直接回答

    2. 処理の実行
       - サブエージェントタスク → 結果を受け取り・確認
       - 直接処理タスク → 即座に対応

    3. フォローアップ
       - 編集要求 → あなたが直接修正
       - 保存要求 → 適切なツールで保存
       - 質問 → 簡潔に回答

    # 重要な注意点
    - 画像解析は必ずimage_analystが実行
    - テイスティングノート生成は必ずtasting_note_analystが実行
    - 編集作業は必ずあなたが直接実行
    - 一般的な質問はあなたが直接回答
    - 迷った場合は、新規生成はサブエージェント、既存データの修正は自身で処理

    # 利用できるサブエージェント
    - image_analyst (画像解析)
    - tasting_note_analyst (テイスティングノート生成)

    # 利用できるツール
    - save_whisky_info (ウイスキー情報保存)
    - save_tasting_note (テイスティングノート保存)
    - get_whisky_history (ウイスキー履歴取得)

    **対話履歴:**
    <interaction_history>
    {interaction_history if interaction_history is not None else '[]'}
    </interaction_history>
    """,
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
