from google.cloud import firestore
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # .env を読み込む

class FirestoreClient:
    """Firestoreとのデータ連携を管理するクラス"""

    def __init__(self):
        self.db = firestore.Client()

    def save_tasting_note(self, user_id: str, tasting_note: dict):
        """
        テイスティングノートをFirestoreに保存する。

        Args:
            user_id (str): ユーザーID。
            tasting_note (dict): 保存するテイスティングノートのデータ。
        """
        doc_ref = self.db.collection("users").document(user_id).collection("whisky_collection").document()
        doc_ref.set(tasting_note)
