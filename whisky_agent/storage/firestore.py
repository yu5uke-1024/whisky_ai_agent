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

    async def get_whisky_history(self, user_id: str = None):
        """ウイスキー履歴を取得（Firestoreが利用できない場合は空のリストを返す）"""
        if self.db is None:
            print("Firestore is not available, returning empty history")
            return []
        
        try:
            if user_id:
                # 特定ユーザーの履歴を取得
                whisky_collection_ref = self.db.collection("users").document(user_id).collection("whisky_collection")
                docs = whisky_collection_ref.stream()
                history = []
                for doc in docs:
                    whisky_data = doc.to_dict()
                    whisky_data['id'] = doc.id
                    history.append(whisky_data)
                print(f"Retrieved {len(history)} whisky records for user {user_id}")
                return history
            else:
                # 全体の履歴を取得（必要に応じて）
                print("No user_id provided, returning empty history")
                return []
        except Exception as e:
            print(f"Failed to get whisky history: {e}")
            return []
    
    def save_conversation_state(self, user_id: str, session_data: dict):
        """会話状態をFirestoreに保存"""
        if self.db is None:
            print("Firestore is not available, skipping conversation state save")
            return
        
        try:
            doc_ref = self.db.collection("user_sessions").document(user_id)
            doc_ref.set({
                "session_data": session_data,
                "last_updated": datetime.now(),
            }, merge=True)
            print(f"Conversation state saved for user {user_id}")
        except Exception as e:
            print(f"Failed to save conversation state: {e}")
    
    def get_conversation_state(self, user_id: str):
        """会話状態をFirestoreから取得"""
        if self.db is None:
            print("Firestore is not available, returning None")
            return None
        
        try:
            doc_ref = self.db.collection("user_sessions").document(user_id)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                print(f"Retrieved conversation state for user {user_id}")
                return data.get("session_data")
            else:
                print(f"No conversation state found for user {user_id}")
                return None
        except Exception as e:
            print(f"Failed to get conversation state: {e}")
            return None

    def save_session_with_id(self, user_id: str, session_id: str, session_data: dict):
        """セッションIDと共に会話状態をFirestoreに保存"""
        if self.db is None:
            print("Firestore is not available, skipping session save")
            return
        
        try:
            doc_ref = self.db.collection("user_sessions").document(user_id)
            doc_ref.set({
                "session_id": session_id,
                "session_data": session_data,
                "last_updated": datetime.now(),
            }, merge=True)
            print(f"Session saved for user {user_id} with session_id {session_id}")
        except Exception as e:
            print(f"Failed to save session: {e}")
    
    def get_session_with_id(self, user_id: str):
        """セッションIDと共に会話状態をFirestoreから取得"""
        if self.db is None:
            print("Firestore is not available, returning None")
            return None, None
        
        try:
            doc_ref = self.db.collection("user_sessions").document(user_id)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                session_id = data.get("session_id")
                session_data = data.get("session_data")
                print(f"Retrieved session for user {user_id}: session_id={session_id}")
                return session_id, session_data
            else:
                print(f"No session found for user {user_id}")
                return None, None
        except Exception as e:
            print(f"Failed to get session: {e}")
            return None, None
