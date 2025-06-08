import os
import asyncio
import tempfile
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from whisky_agent.agent import root_agent
from utils import call_agent_async, add_user_query_to_history, create_or_get_session, initialize_whisky_agent_system

load_dotenv()

print("Starting ADK Multi-Agent LINE Bot server...")

app = FastAPI(title="Whisky AI Multi-Agent LINE Bot", version="1.0.0")

# LINE Bot設定
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# ADK設定（main.pyと同じ構成）
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()
runner = None
APP_NAME = "Whisky Assistant"

# グローバルなユーザーごとのセッション管理（永続化）
user_sessions = {}
user_session_states = {}  # セッション状態をメモリ内で保持

async def get_or_create_session_for_user(user_id: str, user_name: str = None):
    """ユーザーごとのADKセッションを取得または作成（Firestore永続化対応）"""
    global runner
    
    # Runnerの初期化
    if runner is None:
        runner = await initialize_whisky_agent_system(session_service, artifact_service, APP_NAME)
    
    # ユーザーのセッションが存在しない場合は作成/復元
    if user_id not in user_sessions:
        print(f"Creating or restoring ADK session for user {user_id}...")
        
        # Firestoreから既存セッションを復元
        try:
            from whisky_agent.storage.firestore import FirestoreClient
            firestore_client = FirestoreClient()
            existing_session_id, existing_state = firestore_client.get_session_with_id(user_id)
            
            if existing_session_id and existing_state:
                print(f"Restoring session from Firestore: {existing_session_id}")
                # 既存セッションを復元
                session = await session_service.create_session(
                    app_name=APP_NAME,
                    user_id=user_id,
                    session_id=existing_session_id,
                    state=existing_state,
                )
                user_sessions[user_id] = session.id
                user_session_states[user_id] = existing_state
                print(f"ADK Session restored: {session.id}")
                return session.id
        except Exception as e:
            print(f"Failed to restore session from Firestore: {e}")
        
        # 新規セッションを作成
        initial_state = {
            "user_name": user_name or f"user_{user_id[-8:]}",
            "user_id": user_id,
            "interaction_history": [],
        }
        
        new_session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            state=initial_state,
        )
        user_sessions[user_id] = new_session.id
        user_session_states[user_id] = initial_state
        
        # 新規セッションをFirestoreに保存
        try:
            from whisky_agent.storage.firestore import FirestoreClient
            firestore_client = FirestoreClient()
            firestore_client.save_session_with_id(user_id, new_session.id, initial_state)
        except Exception as e:
            print(f"Failed to save new session to Firestore: {e}")
        
        print(f"New ADK Session created: {new_session.id}")
    else:
        # 既存セッションの状態を確認・更新
        try:
            session = await session_service.get_session(
                app_name=APP_NAME, 
                user_id=user_id, 
                session_id=user_sessions[user_id]
            )
            # 最新の状態をローカルキャッシュに保存
            user_session_states[user_id] = session.state
        except Exception as e:
            print(f"Error retrieving session state: {e}")
            # セッションが見つからない場合は再作成
            if user_id in user_sessions:
                del user_sessions[user_id]
            return await get_or_create_session_for_user(user_id, user_name)
    
    return user_sessions[user_id]


async def process_with_multi_agent(user_id: str, query: str, image_data: Optional[bytes] = None) -> str:
    """ADKマルチエージェントシステムでメッセージを処理（main.pyと同じ方法）"""
    try:
        print(f"Processing with ADK multi-agent system - User: {user_id}, Query: {query}")
        
        # ADKセッションを取得または作成
        session_id = await get_or_create_session_for_user(user_id)
        
        # 画像処理
        image_path = None
        if image_data:
            # 一時ファイルとして保存
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(image_data)
                image_path = temp_file.name
            print(f"Image saved for processing: {image_path}")
        
        # ユーザークエリを履歴に追加（main.pyと同じ方法）
        await add_user_query_to_history(
            session_service, APP_NAME, user_id, session_id, query
        )
        
        print(f"Calling ADK root_agent through call_agent_async...")
        
        # main.pyと同じ方法でADKマルチエージェントを呼び出し
        response = await call_agent_async(
            runner, user_id, session_id, query=query, image_path=image_path
        )
        
        # 一時ファイルを削除
        if image_path and os.path.exists(image_path):
            try:
                os.unlink(image_path)
                print(f"Temporary image file deleted: {image_path}")
            except Exception as e:
                print(f"Failed to delete temporary file: {e}")
        
        if response is None or response.strip() == "":
            response = "申し訳ございませんが、ウイスキーエージェントからの応答を取得できませんでした。もう一度お試しください。"
        
        print(f"ADK multi-agent response: {response[:200]}...")
        return response
        
    except Exception as e:
        print(f"Error in ADK multi-agent processing: {e}")
        import traceback
        print(f"Error traceback: {traceback.format_exc()}")
        return f"申し訳ありません。ウイスキーマルチエージェントシステムで処理中にエラーが発生しました: {str(e)}"


@app.get("/health")
async def health_check():
    """ヘルスチェック用エンドポイント"""
    adk_status = "initialized" if runner is not None else "not_initialized"
    return {
        "status": "healthy", 
        "service": "adk_multi_agent_line_bot", 
        "adk_runner": adk_status,
        "ready": True
    }

@app.post("/webhook")
async def handle_webhook(request: Request):
    """LINE Webhook処理"""
    signature = request.headers.get('X-Line-Signature', '')
    body = await request.body()
    
    try:
        handler.handle(body.decode('utf-8'), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """テキストメッセージの受信処理（ADKマルチエージェントシステムで同期処理）"""
    print(f"Received text message: {event.message.text}")
    
    import asyncio
    import threading
    
    def run_async_task():
        try:
            user_id = event.source.user_id
            user_query = event.message.text
            
            print(f"Processing text message with ADK multi-agent - User: {user_id}, Query: {user_query}")
            
            # 新しいイベントループで実行
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # ADKマルチエージェントシステムで処理
                response = loop.run_until_complete(
                    process_with_multi_agent(user_id, user_query)
                )
                
                # LINE Botで返信
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"🥃 {response}")
                )
                print(f"ADK multi-agent response sent successfully for user {user_id}")
                
            finally:
                loop.close()
                
        except Exception as e:
            print(f"Error processing text message: {e}")
            import traceback
            print(f"Error traceback: {traceback.format_exc()}")
            try:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="申し訳ありません。ウイスキーエージェントでエラーが発生しました。もう一度お試しください。")
                )
            except Exception as reply_error:
                print(f"Failed to send error reply: {reply_error}")
    
    # 別スレッドで非同期処理を実行
    thread = threading.Thread(target=run_async_task)
    thread.start()

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    """画像メッセージの受信処理（ADKマルチエージェントシステムで同期処理）"""
    print(f"Received image message from user: {event.source.user_id}")
    
    import asyncio
    import threading
    
    def run_async_task():
        try:
            user_id = event.source.user_id
            
            print(f"Processing image message with ADK multi-agent - User: {user_id}")
            
            # 画像データを取得
            message_content = line_bot_api.get_message_content(event.message.id)
            image_data = b''.join(message_content.iter_content())
            
            print(f"Image data retrieved, size: {len(image_data)} bytes")
            
            # 新しいイベントループで実行
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # ADKマルチエージェントシステムで画像分析
                response = loop.run_until_complete(
                    process_with_multi_agent(user_id, "ウイスキーの画像を分析してください", image_data)
                )
                
                # LINE Botで返信
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"📸🥃 {response}")
                )
                print(f"ADK multi-agent image analysis response sent successfully for user {user_id}")
                
            finally:
                loop.close()
                
        except Exception as e:
            print(f"Error processing image message: {e}")
            import traceback
            print(f"Error traceback: {traceback.format_exc()}")
            try:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="申し訳ありません。ウイスキー画像分析中にエラーが発生しました。もう一度お試しください。")
                )
            except Exception as reply_error:
                print(f"Failed to send image error reply: {reply_error}")
    
    # 別スレッドで非同期処理を実行
    thread = threading.Thread(target=run_async_task)
    thread.start()

print("ADK Multi-Agent LINE Bot server loaded successfully")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    print(f"Starting uvicorn server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

print("ADK Multi-Agent LINE Bot server module loaded successfully")