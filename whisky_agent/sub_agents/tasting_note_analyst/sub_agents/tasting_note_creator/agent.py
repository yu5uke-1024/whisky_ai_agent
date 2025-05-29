from google.adk.agents import Agent
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError
from .prompts import TASTING_NOTE_CREATION_INSTRUCTION
from ...models import TastingAnalysis


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
