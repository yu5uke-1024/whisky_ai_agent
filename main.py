from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from whisky_agent.agent import root_agent
from utils import add_user_query_to_history, call_agent_async
import asyncio
import os

# 環境変数の読み込み
load_dotenv()

# セッションサービスの作成
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()

async def main_async():
    # ユーザー情報の入力
    print("=== Whisky Assistant ===\n")
    user_id = input("ユーザーIDを入力してください: ").strip()
    if not user_id:
        user_id = "default_user"
    
    user_name = input("ユーザー名を入力してください: ").strip()
    if not user_name:
        user_name = "ユーザー"
    
    # 初期状態の設定
    initial_state = {
        "user_name": user_name,
        "interaction_history": [],
    }

    # 新しいセッションの作成
    APP_NAME = "Whisky Assistant"
    USER_ID = user_id
    new_session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    )

    SESSION_ID = new_session.id
    print(f"--- Examining Session Properties ---")
    print(f"ID (`id`):                {new_session.id}")
    print(f"Application Name (`app_name`): {new_session.app_name}")
    print(f"User ID (`user_id`):         {new_session.user_id}")
    print(f"State (`state`):           {new_session.state}") # Note: Only shows initial state here
    print(f"Events (`events`):         {new_session.events}") # Initially empty
    print(f"Last Update (`last_update_time`): {new_session.last_update_time:.2f}")
    print(f"---------------------------------")

    # Runnerの初期化
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
        artifact_service=artifact_service,
    )

    print("\nWhisky Assistant へようこそ!")
    print("終了するには 'exit' または 'quit' と入力してください。\n")

    while True:
        print("\n🗨️ Enter your query (or 'exit' to quit):")
        user_query = input("Query: ").strip()
        if user_query.lower() == "exit":
            break

        image_path = input("Image path (optional): ").strip()
        if image_path == "":
            image_path = None

        # 履歴への追加
        await add_user_query_to_history(session_service, APP_NAME, USER_ID, SESSION_ID, user_query)

        # エージェントの実行
        await call_agent_async(runner, USER_ID, SESSION_ID, query = user_query, image_path=image_path)


    # 最終セッション状態の表示
    final_session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print("\n最終セッション状態:")
    for key, value in final_session.state.items():
        print(f"{key}: {value}")

def main():
    """アプリケーションのエントリーポイント"""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
