from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
from google.genai import types
from google.adk.agents.callback_context import CallbackContext

class TastingAnalysis(BaseModel):
    """テイスティングノートの分析結果またはデータ構造"""
    nose: List[str] = Field(
        description="香りの特徴リスト",
        default_factory=list
    )
    palate: List[str] = Field(
        description="味わいの特徴リスト",
        default_factory=list
    )
    finish: List[str] = Field(
        description="余韻の特徴リスト",
        default_factory=list
    )
    rating: float = Field(
        description="評価 (1-5の数値)",
        ge=1.0,
        le=5.0,
        default=2.5
    )


class WhiskyInfo(BaseModel):
    brand: str = Field(
        description="ブランド名（日本語の正式名称）",
        default=""
    )
    age: str = Field(
        description="熟成年数（年の単位付き、NASの場合は「NAS」）",
        default=""
    )
    distillery: str = Field(
        description="蒸溜所の正式名称（日本語）",
        default=""
    )
    country: str = Field(
        description="生産国",
        default=""
    )
    region: str = Field(
        description="生産地域",
        default=""
    )
    whisky_type: str = Field(
        description="ウイスキーの種類",
        default=""
    )


def create_whisky_id(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    ウイスキーのIDを作成する
    """
    whisky_id = callback_context.state.get("whisky_id", "default_whisky_id")
    callback_context.state["whisky_info"] = {}
    callback_context.state["tasting_note"] = {}

    if whisky_id == "default_whisky_id":
        ##前の情報を削除する必要あり
        whisky_id = str(uuid.uuid4())
        callback_context.state["whisky_id"] = whisky_id
    return None
