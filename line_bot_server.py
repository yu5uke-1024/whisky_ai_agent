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
from utils import call_agent_async, initialize_whisky_agent_system

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

# シンプルなメモリ内セッション管理
active_sessions = {}


def format_line_response(text: str) -> str:
    """
    LINE返信用にテキストを整形する（例: * を除去）
    """
    if not text:
        return ""
    # '*' を除去し、前後の空白も整える
    return text.replace('*', '').strip()

async def get_or_create_session_for_user(user_id: str):
    """ユーザーごとのADKセッションを取得または作成（メモリベース）"""
    global runner

    # Runnerの初期化
    if runner is None:
        runner = await initialize_whisky_agent_system(session_service, artifact_service, APP_NAME)

    # メモリ内にセッションがあるかチェック
    if user_id in active_sessions:
        return active_sessions[user_id]

    # 新規セッション作成
    session_id = f"session_{user_id}"

    try:
        # 初期状態で新規セッション作成
        initial_state = {
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

        # 履歴追加をスキップ（メモリのみセッション管理）

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

        # --- 整形して返信 ---
        formatted_response = format_line_response(response)
        await line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=formatted_response)
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
            "ウイスキーの画像の分析、もしくはメニューの画像からおすすめウイスキーを教えて",
            image_data
        )

        # --- 整形して返信 ---
        formatted_response = format_line_response(response)
        await line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=formatted_response)
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
