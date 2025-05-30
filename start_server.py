#!/usr/bin/env python3
"""
Whisky AI Agent API サーバー起動スクリプト
"""

import uvicorn
import sys
import os

def main():
    """APIサーバーを起動"""
    print("🥃 Whisky AI Agent API サーバーを起動しています...")
    print("📍 サーバーURL: http://localhost:8000")
    print("📖 API ドキュメント: http://localhost:8000/docs")
    print("🔄 ヘルスチェック: http://localhost:8000/health")
    print("⏹️  停止するには Ctrl+C を押してください")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "api_server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # 開発時の自動リロード
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 サーバーを停止しました")
    except Exception as e:
        print(f"❌ サーバー起動エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
