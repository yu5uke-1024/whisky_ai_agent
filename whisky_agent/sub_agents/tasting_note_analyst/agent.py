from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from ...models.tasting import TastingNote

# --- Define Output Schema (also used for current_note in input) ---
class TastingAnalysis(BaseModel):
    nose: List[str] = Field(
        description="List of characteristics detected in the nose/aroma",
        default_factory=list
    )
    palate: List[str] = Field(
        description="List of characteristics detected in the palate/taste",
        default_factory=list
    )
    finish: List[str] = Field(
        description="List of characteristics detected in the finish/aftertaste",
        default_factory=list
    )
    rating: float = Field(
        description="Rating on a scale of 1-5. e.g., 3.5",
        ge=1.0,
        le=5.0,
        default=2.5
    )
    memo: Optional[str] = Field(
        default=None,
        description="Overall analysis and additional notes. e.g., 'Well-balanced with a hint of smoke.'"
    )

# --- Define Input Schema for modification or creation ---
class TastingNoteInput(BaseModel):
    current_note: Optional[TastingAnalysis] = Field(
        default=None,
        description="The existing tasting note to be modified. Provide if updating."
    )
    modification_request: Optional[str] = Field(
        default=None,
        description="User's request detailing the changes. e.g., 'Change nose to apple and honey, rating to 4.0'."
    )
    whisky_name_or_features: Optional[str] = Field(
        default=None,
        description="Name of the whisky or its features for new note creation. e.g., 'Lagavulin 16 year old' or 'smoky and peaty whisky'."
    )

tasting_note_analyst = Agent(
    name="tasting_note_analyst",
    model="gemini-2.0-flash-lite",
    description="ウイスキーのテイスティング分析および修正の専門家",
    instruction="""
    あなたはウイスキーのテイスティング分析の専門家です。
    提供された情報に基づいてテイスティングノートを生成、または既存のテイスティングノートをユーザーの指示に従って修正します。

    入力には、以下のいずれか、または両方が含まれます。
    - `current_note`: 修正対象の既存テイスティングノート。
    - `modification_request`: ユーザーからの具体的な修正指示。
    - `whisky_name_or_features`: 新規作成時のウイスキー名や特徴。

    【新規作成の場合】
    `whisky_name_or_features` に基づいて、以下の分析項目でテイスティングノートを作成してください。
    1. 香り(Nose): アロマ、強度、変化
    2. 味わい(Palate): 第一印象、展開、テクスチャー
    3. 余韻(Finish): 長さ、特徴、印象
    4. 評価(Rating): 1.0から5.0の間の数値。例: 3.5
    5. 総合コメント(Memo): 任意。

    【修正の場合】
    `current_note` (既存のテイスティングノート) と `modification_request` (ユーザーの修正指示) が提供されます。
    `current_note` の内容を `modification_request` に従って変更し、新しい完全なテイスティングノートを生成してください。
    例えば、「香りを『りんご、はちみつ』に変更して、評価を4.0にして」という指示があれば、`current_note` の `nose` と `rating` フィールドを更新し、他のフィールドは元の値をできるだけ維持しつつ、新しい完全なテイスティングノートを返します。
    修正指示が特定の項目のみの場合でも、必ず完全なテイスティングノートの構造で返してください。

    応答は必ず以下のJSON形式で、指定されたキーで返してください。
    {
        "nose": ["特徴1", "特徴2"...],
        "palate": ["特徴1", "特徴2"...],
        "finish": ["特徴1", "特徴2"...],
        "rating": 4.5,
        "memo": "総合コメント"
    }
    """,
    input_schema=TastingNoteInput,
    output_schema=TastingAnalysis,
    output_key="tasting_analysis"
)
