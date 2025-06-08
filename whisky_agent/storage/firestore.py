from google.cloud import firestore
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()  # .env を読み込む

class FirestoreClient:
    """Firestoreとのデータ連携を管理するクラス"""

    def __init__(self):
        # Cloud Run環境ではデフォルト認証を使用
        try:
            # プロジェクトIDを明示的に指定
            project_id = "whisky-ai-project"
            self.db = firestore.Client(project=project_id)
            print(f"Firestore initialized with project: {project_id}")
        except Exception as e:
            print(f"Firestore initialization failed: {e}")
            # フォールバック: Firestoreを無効化
            self.db = None

    def save_whisky_info(self, user_id: str, whisky_id: str, whisky_info: dict):
        """
        ウイスキー情報をFirestoreに更新または追加する。

        Args:
            user_id (str): ユーザーID。
            whisky_id (str): ウイスキーID。
            whisky_info (dict): 更新または追加するウイスキー情報のデータ。
        """
        if self.db is None:
            print("Firestore is not available, skipping save operation")
            return
        
        try:
            doc_ref = self.db.collection("users").document(user_id).collection("whisky_collection").document(whisky_id)
            doc_ref.set(whisky_info, merge=True)
            print(f"Whisky info saved for user {user_id}, whisky {whisky_id}")
        except Exception as e:
            print(f"Failed to save whisky info: {e}")

    async def get_whisky_history(self):
        """ウイスキー履歴を取得（Firestoreが利用できない場合は空のリストを返す）"""
        if self.db is None:
            print("Firestore is not available, returning empty history")
            return []
        
        try:
            # 実際の履歴取得ロジックを実装
            return []
        except Exception as e:
            print(f"Failed to get whisky history: {e}")
            return []
