import os
import tempfile
from typing import Optional
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from whisky_agent.agent import root_agent
from utils import call_agent_async, add_user_query_to_history

# 環境変数の読み込み
load_dotenv()

app = FastAPI(title="Whisky AI Agent API", version="1.0.0")

# CORS設定（Flutter Webからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切なオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# グローバル変数でセッション管理
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()
runner = None
APP_NAME = "Whisky Assistant"
USER_ID = "default_user"
SESSION_ID = None

# 初期状態の設定
initial_state = {
    "user_name": "ユーザー",
    "interaction_history": [],
}

async def initialize_session():
    """セッションとランナーを初期化"""
    global runner, SESSION_ID
    
    if runner is None:
        # 新しいセッションの作成
        new_session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            state=initial_state,
        )
        SESSION_ID = new_session.id
        
        # Runnerの初期化
        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service,
            artifact_service=artifact_service,
        )

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の初期化"""
    await initialize_session()

@app.post("/chat")
async def chat_endpoint(
    query: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    """
    チャットエンドポイント
    
    Args:
        query: ユーザーからのテキストクエリ
        image: 任意の画像ファイル
    
    Returns:
        JSON形式の応答 {"response": "..."}
    """
    try:
        # セッションが初期化されていない場合は初期化
        if runner is None or SESSION_ID is None:
            await initialize_session()
        
        image_path = None
        
        # 画像が提供された場合、一時ファイルとして保存
        if image and image.filename:
            # 画像ファイルの拡張子を取得
            file_extension = os.path.splitext(image.filename)[1].lower()
            if file_extension not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                raise HTTPException(
                    status_code=400, 
                    detail="サポートされていない画像形式です。JPG、PNG、GIF、BMPのみサポートしています。"
                )
            
            # 一時ファイルを作成
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                content = await image.read()
                temp_file.write(content)
                image_path = temp_file.name
        
        # ユーザークエリを履歴に追加
        await add_user_query_to_history(
            session_service, APP_NAME, USER_ID, SESSION_ID, query
        )
        
        # エージェントを呼び出し
        response = await call_agent_async(
            runner, USER_ID, SESSION_ID, query=query, image_path=image_path
        )
        
        # 一時ファイルを削除
        if image_path and os.path.exists(image_path):
            try:
                os.unlink(image_path)
            except Exception as e:
                print(f"一時ファイルの削除に失敗: {e}")
        
        if response is None:
            response = "申し訳ございませんが、応答を生成できませんでした。"
        
        return JSONResponse(
            status_code=200,
            content={"response": response}
        )
        
    except HTTPException:
        # HTTPExceptionはそのまま再発生
        raise
    except Exception as e:
        # その他のエラーをキャッチ
        print(f"チャットエンドポイントでエラーが発生: {e}")
        
        # 一時ファイルが作成されていた場合は削除
        if 'image_path' in locals() and image_path and os.path.exists(image_path):
            try:
                os.unlink(image_path)
            except:
                pass
        
        raise HTTPException(
            status_code=500,
            detail=f"内部サーバーエラーが発生しました: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy", "message": "Whisky AI Agent API is running"}

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Whisky AI Agent API", 
        "version": "1.0.0",
        "endpoints": {
            "chat": "POST /chat - チャット機能",
            "health": "GET /health - ヘルスチェック"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
