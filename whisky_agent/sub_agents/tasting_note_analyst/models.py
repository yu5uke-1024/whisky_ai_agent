from typing import List
from pydantic import BaseModel, Field

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
