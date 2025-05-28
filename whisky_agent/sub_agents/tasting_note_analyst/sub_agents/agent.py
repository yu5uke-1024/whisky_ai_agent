from google.adk.agents import Agent
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError
from .prompts import TASTING_NOTE_CREATION_INSTRUCTION

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

# Input Schema for tasting note creation
class TastingNoteCreationInput(BaseModel):
    """テイスティングノート作成エージェントへの入力スキーマ"""
    whisky_name: str = Field(
        description="新規作成時のウイスキー名や特徴。例: 'Lagavulin 16 year old'."
    )

# テイスティングノート作成エージェントの定義
tasting_note_creator = Agent(
    name="tasting_note_creator",
    model="gemini-2.0-flash-lite",
    description="ウイスキーのテイスティングノート作成の専門家。提供されたウイスキー情報に基づいてノートを生成します。",
    instruction=TASTING_NOTE_CREATION_INSTRUCTION,
    input_schema=TastingNoteCreationInput,
    output_schema=TastingAnalysis,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_key="tasting_note"
)
