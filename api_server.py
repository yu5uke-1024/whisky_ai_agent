from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from contextlib import asynccontextmanager
import base64
import io
from PIL import Image
import asyncio
import os
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from whisky_agent.agent import root_agent, create_agent_with_context
from utils import add_user_query_to_history, call_agent_async
from google.genai import types

# 環境変数の読み込み
load_dotenv()

# グローバル変数でセッション情報を保持
APP_NAME = "Whisky Assistant"
USER_ID = "web_user"
SESSION_ID = None
runner = None
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()

# 初期状態の設定
initial_state = {
    "user_name": "ゲスト",
    "interaction_history": [],
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global SESSION_ID, runner
    
    # 新しいセッションの作成
    new_session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    )
    SESSION_ID = new_session.id
    
    # コンテキスト付きエージェントの作成
    context_agent = create_agent_with_context(
        session_service, APP_NAME, USER_ID, SESSION_ID
    )
    
    # Runnerの初期化
    runner = Runner(
        agent=context_agent,
        app_name=APP_NAME,
        session_service=session_service,
        artifact_service=artifact_service,
    )
    
    print(f"API Server started with context-aware agent. Session ID: {SESSION_ID}")
    
    yield
    
    # Shutdown
    print("API Server shutting down...")

app = FastAPI(
    title="Whisky AI Assistant API", 
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定（Flutterアプリからのリクエストを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切なオリジンを設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    image: Optional[str] = None  # Base64エンコードされた画像
    image_name: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

@app.get("/")
async def root():
    """ヘルスチェック用エンドポイント"""
    return {"message": "Whisky AI Assistant API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """チャットメッセージを処理するエンドポイント"""
    try:
        message = request.message
        
        # 画像がある場合の処理
        if request.image:
            try:
                # Base64デコード
                image_data = base64.b64decode(request.image)
                image = Image.open(io.BytesIO(image_data))
                
                # 画像を一時的に保存（実際の実装では適切な画像処理を行う）
                temp_image_path = f"temp_{request.image_name or 'image.jpg'}"
                image.save(temp_image_path)
                
                # 画像解析のメッセージを追加
                if not message or message == "画像を解析してください":
                    message = "この画像のウイスキーを解析してください"
                
                # 一時ファイルを削除
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)
                    
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"画像の処理中にエラーが発生しました: {str(e)}")
        
        # 履歴への追加
        await add_user_query_to_history(
            session_service, APP_NAME, USER_ID, SESSION_ID, message
        )
        
        # エージェントの実行（改良されたcall_agent_async関数を使用）
        response_text = await call_agent_async(runner, USER_ID, SESSION_ID, message)
        
        if not response_text:
            response_text = "申し訳ございませんが、適切な回答を生成できませんでした。"
        
        return ChatResponse(response=response_text)
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"内部サーバーエラー: {str(e)}")

async def call_agent_async_api(runner, user_id, session_id, query):
    """API用のエージェント呼び出し関数"""
    content = types.Content(role="user", parts=[types.Part(text=query)])
    final_response_text = None
    agent_name = None

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            # Capture the agent name from the event if available
            if event.author:
                agent_name = event.author

            # Only process and display the final response
            if event.is_final_response():
                if (
                    event.content
                    and event.content.parts
                    and hasattr(event.content.parts[0], "text")
                    and event.content.parts[0].text
                ):
                    final_response_text = event.content.parts[0].text.strip()
                    break
    except Exception as e:
        print(f"ERROR during agent run: {e}")
        final_response_text = f"エージェントの実行中にエラーが発生しました: {str(e)}"

    # Add the agent response to interaction history if we got a final response
    if final_response_text and agent_name:
        from utils import add_agent_response_to_history
        await add_agent_response_to_history(
            runner.session_service,
            runner.app_name,
            user_id,
            session_id,
            agent_name,
            final_response_text,
        )

    return final_response_text

@app.get("/history")
async def get_history():
    """会話履歴を取得するエンドポイント"""
    try:
        session = await session_service.get_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        return {"history": session.state.get("interaction_history", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"履歴の取得中にエラーが発生しました: {str(e)}")

@app.delete("/history")
async def clear_history():
    """会話履歴をクリアするエンドポイント"""
    try:
        global SESSION_ID
        # 新しいセッションを作成
        new_session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            state=initial_state,
        )
        SESSION_ID = new_session.id
        return {"message": "履歴がクリアされました", "new_session_id": SESSION_ID}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"履歴のクリア中にエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
