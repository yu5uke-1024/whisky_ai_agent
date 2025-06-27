from google.cloud import firestore
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
import random

load_dotenv()  # .env を読み込む

class FirestoreClient:
    """Firestoreとのデータ連携を管理するクラス"""

    def __init__(self):
        # Cloud Run環境判定：GOOGLE_APPLICATION_CREDENTIALSがローカルファイルを指している場合は無視
        try:
            project_id = "whisky-ai-project"

            # Cloud Run環境では環境変数を削除してデフォルト認証を使用
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if credentials_path and not os.path.exists(credentials_path):
                # ファイルが存在しない場合は環境変数をクリア（Cloud Run環境）
                os.environ.pop('GOOGLE_APPLICATION_CREDENTIALS', None)
                print("Removed GOOGLE_APPLICATION_CREDENTIALS for Cloud Run environment")

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
        JST = timezone(timedelta(hours=9))
        if self.db is None:
            print("Firestore is not available, skipping save operation")
            return

        try:
            # JSTの現在時刻を取得
            whisky_info_with_timestamp = whisky_info.copy()
            whisky_info_with_timestamp["updated_at"] = datetime.now(JST)
            doc_ref = self.db.collection("users").document(user_id).collection("whisky_collection").document(whisky_id)
            doc_ref.set(whisky_info_with_timestamp, merge=True)
            print(f"Whisky info saved for user {user_id}, whisky {whisky_id}")
        except Exception as e:
            print(f"Failed to save whisky info: {e}")

    def _get_whisky_collection_for_user(self, user_id: str) -> list:
        """指定されたユーザーのウイスキーコレクションを取得する内部メソッド"""
        whisky_collection_ref = self.db.collection("users").document(user_id).collection("whisky_collection")
        docs = whisky_collection_ref.stream()
        history = []
        for doc in docs:
            whisky_data = doc.to_dict()
            whisky_data['id'] = doc.id
            history.append(whisky_data)
        return history

    def _get_random_user_id(self, exclude_user_id: str = None) -> str:
        """ランダムなユーザーIDを取得する内部メソッド（指定されたユーザーIDを除外）"""
        users_ref = self.db.collection("users")
        user_docs = users_ref.list_documents()
        user_ids = [doc.id for doc in user_docs]

        if not user_ids:
            raise ValueError("No users found in Firestore")

        # 除外するユーザーIDがある場合は、それ以外のユーザーIDから選択
        if exclude_user_id and exclude_user_id in user_ids:
            available_user_ids = [uid for uid in user_ids if uid != exclude_user_id]
            if not available_user_ids:
                raise ValueError("No other users found in Firestore")
            return random.choice(available_user_ids)

        return random.choice(user_ids)
    
    async def get_whisky_history(self, user_id: str = None, exclude_user_id: str = None):
        """ウイスキー履歴を取得（Firestoreが利用できない場合は空のリストを返す）"""
        if self.db is None:
            print("Firestore is not available, returning empty history")
            return []

        try:
            if user_id:
                # 特定ユーザーの履歴を取得
                history = self._get_whisky_collection_for_user(user_id)
                print(f"Retrieved {len(history)} whisky records for user {user_id}")
                return history
            else:
                # 他のユーザーIDからランダムに選択して履歴を取得
                try:
                    random_user_id = self._get_random_user_id(exclude_user_id)
                    print(f"Selected random user_id: {random_user_id}")

                    history = self._get_whisky_collection_for_user(random_user_id)
                    print(f"Retrieved {len(history)} whisky records for random user {random_user_id}")
                    return history

                except ValueError as e:
                    print(f"No users found: {e}")
                    return []
                except Exception as e:
                    print(f"Failed to get random user history: {e}")
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
