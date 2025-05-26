from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext
# from .storage.firestore import FirestoreClient
from .models.whisky import WhiskyInfo
from .models.tasting import TastingNote
from .sub_agents.image_analyst import image_analyst
from .sub_agents.tasting_note_analyst import tasting_note_analyst

# Firestoreクライアントのインスタンスを作成
# firestore_client = FirestoreClient()

async def save_whisky_info(whisky_info: dict, tool_context: ToolContext) -> dict:
    """ウイスキー情報を保存するツール"""
    try:
        whisky = WhiskyInfo(
            name=whisky_info.get('brand', '不明'),
            image_analysis=whisky_info
        )
        # whisky_id = await firestore_client.save_whisky(whisky)
        whisky_id = "123"
        
        # セッション状態にウイスキー情報を保存
        session = await tool_context.session_service.get_session(
            app_name=tool_context.app_name,
            user_id=tool_context.user_id,
            session_id=tool_context.session_id
        )
        
        # 保存されたウイスキー情報をstateに追加
        saved_whiskies = session.state.get("saved_whiskies", [])
        saved_whiskies.append({
            "whisky_id": whisky_id,
            "info": whisky_info,
            "timestamp": tool_context.timestamp
        })
        
        updated_state = session.state.copy()
        updated_state["saved_whiskies"] = saved_whiskies
        
        await tool_context.session_service.create_session(
            app_name=tool_context.app_name,
            user_id=tool_context.user_id,
            session_id=tool_context.session_id,
            state=updated_state,
        )
        
        return {
            "status": "success",
            "whisky_id": whisky_id,
            "message": "ウイスキー情報を保存しました"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def save_tasting_note(note_info: dict, tool_context: ToolContext) -> dict:
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
        
        # セッション状態にテイスティングノートを保存
        session = await tool_context.session_service.get_session(
            app_name=tool_context.app_name,
            user_id=tool_context.user_id,
            session_id=tool_context.session_id
        )
        
        # 保存されたテイスティングノートをstateに追加
        saved_notes = session.state.get("saved_tasting_notes", [])
        saved_notes.append({
            "note_id": note_id,
            "note": note_info,
            "timestamp": tool_context.timestamp
        })
        
        updated_state = session.state.copy()
        updated_state["saved_tasting_notes"] = saved_notes
        
        await tool_context.session_service.create_session(
            app_name=tool_context.app_name,
            user_id=tool_context.user_id,
            session_id=tool_context.session_id,
            state=updated_state,
        )
        
        return {
            "status": "success",
            "note_id": note_id,
            "message": "テイスティングノートを保存しました"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def get_whisky_history(tool_context: ToolContext) -> dict:
    """ウイスキーの履歴を取得するツール"""
    try:
        # セッション状態から保存されたウイスキー情報を取得
        session = await tool_context.session_service.get_session(
            app_name=tool_context.app_name,
            user_id=tool_context.user_id,
            session_id=tool_context.session_id
        )
        
        saved_whiskies = session.state.get("saved_whiskies", [])
        saved_notes = session.state.get("saved_tasting_notes", [])
        
        # history = await firestore_client.get_whisky_history()
        return {
            "status": "success",
            "saved_whiskies": saved_whiskies,
            "saved_tasting_notes": saved_notes,
            "message": f"保存されたウイスキー: {len(saved_whiskies)}件, テイスティングノート: {len(saved_notes)}件"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def create_agent_with_context(session_service, app_name, user_id, session_id):
    """セッション状態を考慮してエージェントを作成する関数"""
    
    async def get_context_info(tool_context: ToolContext) -> dict:
        """
        セッションから会話履歴とサブエージェント結果を取得するツール
        
        Returns:
            dict: 会話履歴と関連情報を含む辞書
        """
        try:
            session = await tool_context.session_service.get_session(
                app_name=tool_context.app_name,
                user_id=tool_context.user_id,
                session_id=tool_context.session_id
            )
            
            interaction_history = session.state.get("interaction_history", [])
            sub_agent_results = session.state.get("sub_agent_results", [])
            saved_whiskies = session.state.get("saved_whiskies", [])
            saved_notes = session.state.get("saved_tasting_notes", [])
            
            # 履歴を読みやすい形式に変換
            formatted_history = []
            for item in interaction_history:
                if item.get("action") == "user_query":
                    formatted_history.append(f"ユーザー: {item.get('query', '')}")
                elif item.get("action") == "agent_response":
                    formatted_history.append(f"アシスタント: {item.get('response', '')}")
            
            history_text = "\n".join(formatted_history[-10:]) if formatted_history else "履歴なし"
            
            return {
                "status": "success",
                "formatted_conversation": history_text,
                "total_interactions": len(interaction_history),
                "saved_whiskies_count": len(saved_whiskies),
                "saved_notes_count": len(saved_notes),
                "sub_agent_results_count": len(sub_agent_results),
                "message": f"会話履歴を取得しました。最新の会話:\n{history_text}"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # 基本のinstruction
    base_instruction = """
    あなたはウイスキー情報の統括コーディネーターです。
    明確な役割分担に基づいて、タスクを適切に振り分けてください。

    # 重要: 会話履歴の活用
    - ユーザーからの質問や要求に対して、以下の場合は必ずget_context_infoツールを使用して過去の会話履歴を確認してください：
      * 「先ほど」「さっき」「前に」「これまで」などの過去を参照する表現がある場合
      * 「履歴」「会話」「やりとり」などの履歴に関する質問の場合
      * 継続的な会話の文脈が必要な場合
    - 履歴に関連する情報がある場合は、それを踏まえて回答してください
    - 継続的な会話の文脈を理解して、適切な回答を提供してください

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
    1. 履歴確認の判断
       - 過去参照表現や履歴関連の質問 → まずget_context_infoで履歴確認
       - 関連する情報があれば、それを踏まえて処理を進める

    2. 入力タイプの判別
       - 画像添付あり → 必ずimage_analystへ
       - テイスティングノート作成要求 → 必ずtasting_note_analystへ
       - 既存データの編集要求 → あなたが直接処理
       - 一般的な質問 → あなたが直接回答

    3. 処理の実行
       - サブエージェントタスク → 結果を受け取り・確認
       - 直接処理タスク → 即座に対応

    4. フォローアップ
       - 編集要求 → あなたが直接修正
       - 保存要求 → 適切なツールで保存
       - 質問 → 簡潔に回答

    # 重要な注意点
    - 画像解析は必ずimage_analystが実行
    - テイスティングノート生成は必ずtasting_note_analystが実行
    - 編集作業は必ずあなたが直接実行
    - 一般的な質問はあなたが直接回答
    - 迷った場合は、新規生成はサブエージェント、既存データの修正は自身で処理
    - 過去の会話履歴を必ず参考にして、文脈に応じた適切な回答を提供してください
    - 継続的な会話として自然な応答を心がけてください

    # 利用できるサブエージェント
    - image_analyst (画像解析)
    - tasting_note_analyst (テイスティングノート生成)

    # 利用できるツール
    - get_context_info (会話履歴とコンテキスト情報取得) ★重要★
    - save_whisky_info (ウイスキー情報保存)
    - save_tasting_note (テイスティングノート保存)
    - get_whisky_history (ウイスキー履歴取得)
    """
    
    return Agent(
        name="whisky_agent",
        model="gemini-2.5-flash-preview-05-20",
        description="Whisky analysis coordinator with clear agent delegation rules",
        instruction=base_instruction,
        tools=[
            save_whisky_info,
            save_tasting_note,
            get_whisky_history,
            get_context_info,
            AgentTool(tasting_note_analyst),
            AgentTool(image_analyst),
        ],
    )

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
    {interaction_history?}
    """,
     sub_agents=[
         image_analyst,
     ],
    tools=[
        save_whisky_info,
        save_tasting_note,
        get_whisky_history,
        AgentTool(tasting_note_analyst),
        #AgentTool(image_analyst),
    ],
)
