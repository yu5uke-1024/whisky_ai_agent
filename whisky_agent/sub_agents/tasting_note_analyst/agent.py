from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from ...models.tasting import TastingNote

# --- Define Output Schema ---
class TastingAnalysis(BaseModel):
    nose: List[str] = Field(
        description="List of characteristics detected in the nose/aroma"
    )
    palate: List[str] = Field(
        description="List of characteristics detected in the palate/taste"
    )
    finish: List[str] = Field(
        description="List of characteristics detected in the finish/aftertaste"
    )
    rating: float = Field(
        description="Rating on a scale of 1-5",
        ge=1.0,
        le=5.0,
        default=2.5
    )

tasting_note_analyst = Agent(
    name="tasting_note_analyst",
    model="gemini-2.0-flash-lite",
    description="ウイスキーのテイスティング分析の専門家",
    instruction="""
    あなたはウイスキーのテイスティング分析の専門家です。

    分析項目:
    1. 香り(Nose): アロマ、強度、変化
    2. 味わい(Palate): 第一印象、展開、テクスチャー
    3. 余韻(Finish): 長さ、特徴、印象
    4. 評価: 5段階評価と特記事項

    応答形式:
    {
        "nose": ["特徴1", "特徴2"...],
        "palate": ["特徴1", "特徴2"...],
        "finish": ["特徴1", "特徴2"...],
        "rating": "1点から5点の評価",
    }
    """,
    output_schema=TastingAnalysis,
    output_key="tasting_analysis"
)
