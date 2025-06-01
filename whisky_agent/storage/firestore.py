from google.cloud import firestore
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # .env を読み込む

class FirestoreClient:
    """Firestoreとのデータ連携を管理するクラス"""

    def __init__(self):
        self.db = firestore.Client()

    def save_whisky_info(self, user_id: str, whisky_id: str, whisky_info: dict):
        """
        ウイスキー情報をFirestoreに更新または追加する。

        Args:
            user_id (str): ユーザーID。
            whisky_id (str): ウイスキーID。
            whisky_info (dict): 更新または追加するウイスキー情報のデータ。
        """
        doc_ref = self.db.collection("users").document(user_id).collection("whisky_collection").document(whisky_id)
        doc_ref.set(whisky_info, merge=True)
