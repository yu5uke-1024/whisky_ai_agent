from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from whisky_agent.agent import root_agent
from utils import add_user_query_to_history, call_agent_async, create_or_get_session, initialize_whisky_agent_system
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
        user_id = "default_user_id"

    # 初期状態の設定
    initial_state = {
        "interaction_history": [],
    }

    APP_NAME = "Whisky Assistant"

    # 統一された関数でセッション作成
    new_session = await create_or_get_session(session_service, APP_NAME, user_id)
    SESSION_ID = new_session.id

    print(f"--- Examining Session Properties ---")
    print(f"ID (`id`):                {new_session.id}")
    print(f"Application Name (`app_name`): {new_session.app_name}")
    print(f"User ID (`user_id`):         {new_session.user_id}")
    print(f"State (`state`):           {new_session.state}")
    print(f"Events (`events`):         {new_session.events}")
    print(f"Last Update (`last_update_time`): {new_session.last_update_time:.2f}")
    print(f"---------------------------------")

    # 統一された関数でRunner初期化
    runner = await initialize_whisky_agent_system(session_service, artifact_service, APP_NAME)

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
        await add_user_query_to_history(session_service, APP_NAME, user_id, SESSION_ID, user_query)

        # エージェントの実行
        await call_agent_async(runner, user_id, SESSION_ID, query = user_query, image_path=image_path)


    # 最終セッション状態の表示
    final_session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
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
