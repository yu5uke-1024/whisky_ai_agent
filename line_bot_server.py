import os
import asyncio
import tempfile
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from linebot.aiohttp_async_http_client import AiohttpAsyncHttpClient
from linebot import AsyncLineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage
from dotenv import load_dotenv
import aiohttp
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from whisky_agent.agent import root_agent
from utils import call_agent_async, add_user_query_to_history, create_or_get_session, initialize_whisky_agent_system

load_dotenv()

print("Starting ADK Multi-Agent LINE Bot server...")

app = FastAPI(title="Whisky AI Multi-Agent LINE Bot", version="1.0.0")

# LINE Bot設定 - 非同期版に変更
session = aiohttp.ClientSession()
async_http_client = AiohttpAsyncHttpClient(session)
line_bot_api = AsyncLineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'), async_http_client)
parser = WebhookParser(os.getenv('LINE_CHANNEL_SECRET'))

# ADK設定
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()
runner = None
APP_NAME = "Whisky Assistant"

# シンプルなメモリ内セッション管理（main.pyと同様）
active_sessions = {}
session_cache = {}  # Firestoreデータのキャッシュ

async def get_or_create_session_for_user(user_id: str):
    """ユーザーごとのADKセッションを取得または作成（最適化版）"""
    global runner

    # Runnerの初期化
    if runner is None:
        runner = await initialize_whisky_agent_system(session_service, artifact_service, APP_NAME)

    # キャッシュされたセッションがあるかチェック
    if user_id in active_sessions:
        return active_sessions[user_id]

    # 新規セッション作成（シンプル化）
    session_id = f"session_{user_id}"
    
    try:
        # Firestoreから復元を試行（非同期で並行実行しない）
        existing_state = None
        if user_id in session_cache:
            existing_state = session_cache[user_id]
        else:
            # バックグラウンドでFirestoreから取得（ブロックしない）
            asyncio.create_task(load_session_from_firestore(user_id))
        
        # 初期状態でセッション作成
        initial_state = existing_state or {
            "user_id": user_id,
            "interaction_history": [],
        }

        new_session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
            state=initial_state,
        )
        
        active_sessions[user_id] = new_session.id
        session_cache[user_id] = initial_state
        
        # バックグラウンドでFirestoreに保存（ブロックしない）
        asyncio.create_task(save_session_to_firestore(user_id, new_session.id, initial_state))
        
        print(f"Session created for user {user_id}: {new_session.id}")
        return new_session.id
        
    except Exception as e:
        print(f"Error creating session for user {user_id}: {e}")
        # フォールバック：最小限のセッション作成
        fallback_session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        active_sessions[user_id] = fallback_session.id
        return fallback_session.id

async def load_session_from_firestore(user_id: str):
    """バックグラウンドでFirestoreからセッションを読み込み"""
    try:
        from whisky_agent.storage.firestore import FirestoreClient
        firestore_client = FirestoreClient()
        _, existing_state = firestore_client.get_session_with_id(user_id)
        if existing_state:
            session_cache[user_id] = existing_state
            print(f"Session loaded from Firestore for user {user_id}")
    except Exception as e:
        print(f"Background Firestore load failed for user {user_id}: {e}")

async def save_session_to_firestore(user_id: str, session_id: str, state: dict):
    """バックグラウンドでFirestoreにセッションを保存"""
    try:
        from whisky_agent.storage.firestore import FirestoreClient
        firestore_client = FirestoreClient()
        firestore_client.save_session_with_id(user_id, session_id, state)
        print(f"Session saved to Firestore for user {user_id}")
    except Exception as e:
        print(f"Background Firestore save failed for user {user_id}: {e}")

async def process_with_multi_agent(user_id: str, query: str, image_data: Optional[bytes] = None) -> str:
    """ADKマルチエージェントシステムでメッセージを処理（最適化版）"""
    try:
        print(f"Processing with ADK multi-agent system - User: {user_id}, Query: {query[:50]}...")

        # ADKセッションを取得または作成
        session_id = await get_or_create_session_for_user(user_id)

        # 画像処理（メモリ内で処理、ファイルI/Oを避ける）
        image_path = None
        if image_data:
            # 一時ファイル作成を最小限に
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(image_data)
                image_path = temp_file.name

        # 履歴追加をスキップ（パフォーマンス優先）
        # await add_user_query_to_history(session_service, APP_NAME, user_id, session_id, query)

        # ADKマルチエージェントを呼び出し
        response = await call_agent_async(
            runner, user_id, session_id, query=query, image_path=image_path
        )

        # 一時ファイル削除
        if image_path and os.path.exists(image_path):
            try:
                os.unlink(image_path)
            except Exception as e:
                print(f"Failed to delete temporary file: {e}")

        if not response or response.strip() == "":
            response = "申し訳ございませんが、応答を取得できませんでした。もう一度お試しください。"

        print(f"ADK response generated successfully for user {user_id}")
        return response

    except Exception as e:
        print(f"Error in ADK multi-agent processing: {e}")
        return f"申し訳ありません。処理中にエラーが発生しました: {str(e)}"

@app.get("/health")
async def health_check():
    """ヘルスチェック用エンドポイント"""
    adk_status = "initialized" if runner is not None else "not_initialized"
    return {
        "status": "healthy",
        "service": "adk_multi_agent_line_bot",
        "adk_runner": adk_status,
        "active_sessions": len(active_sessions),
        "ready": True
    }

@app.post("/webhook")
async def handle_webhook(request: Request):
    """LINE Webhook処理（完全非同期版）"""
    signature = request.headers.get('X-Line-Signature', '')
    body = await request.body()
    body_text = body.decode('utf-8')

    try:
        events = parser.parse(body_text, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 全てのイベントを並行処理
    tasks = []
    for event in events:
        if isinstance(event, MessageEvent):
            if isinstance(event.message, TextMessage):
                tasks.append(handle_text_message_async(event))
            elif isinstance(event.message, ImageMessage):
                tasks.append(handle_image_message_async(event))
    
    # 全てのタスクを並行実行
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

    return "OK"

async def handle_text_message_async(event):
    """テキストメッセージの非同期処理"""
    try:
        user_id = event.source.user_id
        user_query = event.message.text

        print(f"Processing text message - User: {user_id}, Query: {user_query[:50]}...")

        # ADKマルチエージェントシステムで処理
        response = await process_with_multi_agent(user_id, user_query)

        # 非同期でLINE Botに返信
        await line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
        print(f"Text response sent successfully for user {user_id}")

    except Exception as e:
        print(f"Error processing text message: {e}")
        try:
            await line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="申し訳ありません。エラーが発生しました。もう一度お試しください。")
            )
        except Exception as reply_error:
            print(f"Failed to send error reply: {reply_error}")

async def handle_image_message_async(event):
    """画像メッセージの非同期処理"""
    try:
        user_id = event.source.user_id
        print(f"Processing image message - User: {user_id}")

        # 非同期で画像データを取得
        message_content = await line_bot_api.get_message_content(event.message.id)
        image_data = b''
        async for chunk in message_content.iter_content():
            image_data += chunk

        print(f"Image data retrieved, size: {len(image_data)} bytes")

        # ADKマルチエージェントシステムで画像分析
        response = await process_with_multi_agent(
            user_id, 
            "ウイスキーの画像を分析してください", 
            image_data
        )

        # 非同期でLINE Botに返信
        await line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
        print(f"Image analysis response sent successfully for user {user_id}")

    except Exception as e:
        print(f"Error processing image message: {e}")
        try:
            await line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="申し訳ありません。画像分析中にエラーが発生しました。もう一度お試しください。")
            )
        except Exception as reply_error:
            print(f"Failed to send image error reply: {reply_error}")

# アプリケーション終了時のクリーンアップ
@app.on_event("shutdown")
async def shutdown_event():
    """アプリケーション終了時の処理"""
    if session:
        await session.close()
    print("Application shutdown completed")

print("ADK Multi-Agent LINE Bot server loaded successfully")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    print(f"Starting uvicorn server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)