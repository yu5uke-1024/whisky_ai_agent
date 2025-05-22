from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from whisky_agent.agent import root_agent
from utils import add_user_query_to_history, call_agent_async
import asyncio
import os

# 環境変数の読み込み
load_dotenv()

# セッションサービスの作成
session_service = InMemorySessionService()

# 初期状態の設定
initial_state = {
    "user_name": "ゲスト",
    "preferences": {},
    "history": []
}

async def main_async():
    # 新しいセッションの作成
    APP_NAME = "Whisky Assistant"
    USER_ID = "default_user"
    new_session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    )
    SESSION_ID = new_session.id
    print(f"セッション作成: {SESSION_ID}")

    # Runnerの初期化
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    print("\nWhisky Assistant へようこそ!")
    print("終了するには 'exit' または 'quit' と入力してください。\n")

    while True:
        try:
            # ユーザー入力の受け取り
            user_input = input("あなた: ")

            # 終了判定
            if user_input.lower() in ["exit", "quit"]:
                print("会話を終了します。ありがとうございました！")
                break

            # 履歴への追加
            add_user_query_to_history(
                session_service, APP_NAME, USER_ID, SESSION_ID, user_input
            )

            # エージェントの実行
            await call_agent_async(runner, USER_ID, SESSION_ID, user_input)

        except Exception as e:
            print(f"エラーが発生しました: {e}")

    # 最終セッション状態の表示
    final_session = session_service.get_session(
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
