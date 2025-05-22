# from google.cloud import firestore
# from ..models.whisky import WhiskyInfo
# from ..models.tasting import TastingNote
# from typing import List, Optional
# from datetime import datetime

# class FirestoreClient:
#     """Firestoreとのデータ連携を管理するクラス"""

#     def __init__(self):
#         self.db = firestore.Client()
#         self.whiskies_collection = self.db.collection('whiskies')
#         self.tasting_notes_collection = self.db.collection('tasting_notes')

#     async def save_whisky(self, whisky: WhiskyInfo) -> str:
#         """ウイスキー情報を保存"""
#         doc_ref = self.whiskies_collection.document(whisky.id)
#         doc_ref.set(whisky.model_dump())
#         return whisky.id

#     async def get_whisky(self, whisky_id: str) -> Optional[WhiskyInfo]:
#         """ウイスキー情報を取得"""
#         doc = self.whiskies_collection.document(whisky_id).get()
#         return WhiskyInfo(**doc.to_dict()) if doc.exists else None

#     async def get_whisky_history(self, limit: int = 10) -> List[WhiskyInfo]:
#         """ウイスキーの履歴を取得"""
#         docs = (self.whiskies_collection
#                .order_by('created_at', direction=firestore.Query.DESCENDING)
#                .limit(limit)
#                .stream())
#         return [WhiskyInfo(**doc.to_dict()) for doc in docs]

#     async def save_tasting_note(self, note: TastingNote) -> str:
#         """テイスティングノートを保存"""
#         doc_ref = self.tasting_notes_collection.document(note.id)
#         doc_ref.set(note.model_dump())
#         return note.id

#     async def get_tasting_notes(self, whisky_id: str) -> List[TastingNote]:
#         """特定のウイスキーのテイスティングノートを取得"""
#         docs = (self.tasting_notes_collection
#                .where('whisky_id', '==', whisky_id)
#                .order_by('created_at', direction=firestore.Query.DESCENDING)
#                .stream())
#         return [TastingNote(**doc.to_dict()) for doc in docs]
