from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

class WhiskyInfo(BaseModel):
    """ウイスキー情報を管理するモデル"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(description="ウイスキーの名称（例：山崎 12年）")
    image_url: Optional[str] = Field(description="画像のURL", default=None)
    image_analysis: Optional[Dict[str, Any]] = Field(description="画像解析結果", default=None)
    memo: Optional[str] = Field(description="メモ", default=None)
    created_at: datetime = Field(default_factory=datetime.now)
