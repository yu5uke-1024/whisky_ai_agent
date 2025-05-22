from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
import uuid

class TastingNote(BaseModel):
    """テイスティングノートを管理するモデル"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    whisky_id: str = Field(description="関連するWhiskyInfoのID")
    nose: List[str] = Field(description="香りの特徴", default_factory=list)
    palate: List[str] = Field(description="味わいの特徴", default_factory=list)
    finish: List[str] = Field(description="余韻の特徴", default_factory=list)
    rating: Optional[float] = Field(description="評価（0-5）", default=None)
    memo: Optional[str] = Field(description="メモ", default=None)
    created_at: datetime = Field(default_factory=datetime.now)
