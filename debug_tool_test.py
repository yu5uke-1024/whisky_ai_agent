#!/usr/bin/env python3
"""
ツールの動作をデバッグするスクリプト
"""

import asyncio
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.tools.tool_context import ToolContext
from whisky_agent.agent import create_agent_with_context

# 環境変数の読み込み
load_dotenv()

async def debug_tool():
    """ツールの動作をデバッグする"""
    
    # セッションサービスの作成
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()

    # 初期状態の設定
    initial_state = {
        "user_name": "デバッグユーザー",
        "interaction_history": [
            {"action": "user_query", "query": "テスト質問1", "timestamp": "2025-05-27 00:00:01"},
            {"action": "agent_response", "response": "テスト回答1", "timestamp": "2025-05-27 00:00:02"},
            {"action": "user_query", "query": "テスト質問2", "timestamp": "2025-05-27 00:00:03"},
            {"action": "agent_response", "response": "テスト回答2", "timestamp": "2025-05-27 00:00:04"},
        ],
        "saved_whiskies": [],
        "saved_tasting_notes": [],
        "sub_agent_results": []
    }

    # 新しいセッションの作成
    APP_NAME = "Debug Test"
    USER_ID = "debug_user"
    new_session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    )

    SESSION_ID = new_session.id
    print(f"デバッグセッション作成: {SESSION_ID}")

    # コンテキスト付きエージェントの作成
    context_agent = create_agent_with_context(
        session_service, APP_NAME, USER_ID, SESSION_ID
    )
    
    # ツールを直接テスト
    print("\n=== ツール直接テスト ===")
    
    # ToolContextを手動で作成
    tool_context = ToolContext(
        session_service=session_service,
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        timestamp=1234567890
    )
    
    # get_context_infoツールを直接呼び出し
    try:
        # エージェントからツールを取得
        get_context_info_tool = None
        for tool in context_agent.tools:
            if hasattr(tool, '__name__') and tool.__name__ == 'get_context_info':
                get_context_info_tool = tool
                break
        
        if get_context_info_tool:
            print("get_context_infoツールを直接実行...")
            result = await get_context_info_tool(tool_context)
            print(f"結果: {result}")
        else:
            print("get_context_infoツールが見つかりません")
            
    except Exception as e:
        print(f"ツール実行エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_tool())
