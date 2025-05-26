#!/usr/bin/env python3
"""
会話の連続性をテストするスクリプト
"""

import asyncio
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from whisky_agent.agent import create_agent_with_context
from utils import add_user_query_to_history, call_agent_async
from google.genai import types

# 環境変数の読み込み
load_dotenv()

async def test_conversation_continuity():
    """会話の連続性をテストする"""
    
    # セッションサービスの作成
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()

    # 初期状態の設定
    initial_state = {
        "user_name": "テストユーザー",
        "interaction_history": [],
    }

    # 新しいセッションの作成
    APP_NAME = "Whisky Assistant Test"
    USER_ID = "test_user"
    new_session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    )

    SESSION_ID = new_session.id
    print(f"テストセッション作成: {SESSION_ID}")

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

    # テストシナリオ
    test_queries = [
        "こんにちは！ウイスキーについて教えてください。",
        "山崎12年について詳しく教えてください。",
        "先ほど話した山崎12年のテイスティングノートを作成してください。",
        "これまでの会話の履歴を教えてください。",
        "保存されているウイスキー情報を確認してください。"
    ]

    print("\n=== 会話連続性テスト開始 ===\n")

    for i, query in enumerate(test_queries, 1):
        print(f"\n--- テスト {i}: {query} ---")
        
        # 履歴への追加
        await add_user_query_to_history(
            session_service, APP_NAME, USER_ID, SESSION_ID, query
        )

        # エージェントの実行
        response = await call_agent_async(runner, USER_ID, SESSION_ID, query)
        
        print(f"レスポンス: {response}")
        print("-" * 50)

    # 最終セッション状態の表示
    final_session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    print("\n=== 最終セッション状態 ===")
    for key, value in final_session.state.items():
        if key == "interaction_history":
            print(f"{key}: {len(value)}件の履歴")
        elif key == "sub_agent_results":
            print(f"{key}: {len(value)}件のサブエージェント結果")
        elif key == "saved_whiskies":
            print(f"{key}: {len(value)}件の保存ウイスキー")
        elif key == "saved_tasting_notes":
            print(f"{key}: {len(value)}件のテイスティングノート")
        else:
            print(f"{key}: {value}")

    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    asyncio.run(test_conversation_continuity())
