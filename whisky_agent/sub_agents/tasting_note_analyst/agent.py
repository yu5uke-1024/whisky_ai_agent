from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any
from ...models.tasting import TastingNote

def analyze_tasting(input_text: str, tool_context: ToolContext) -> Dict[str, Any]:
    """テイスティングノートを分析するツール"""
    try:
        # 入力テキストから情報を抽出
        return {
            "status": "success",
            "analysis": {
                "nose": ["分析された香りの特徴"],
                "palate": ["分析された味わいの特徴"],
                "finish": ["分析された余韻の特徴"],
                "rating": 4.5,
                "memo": "総合的な分析結果"
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

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
        "rating": 4.5,
        "memo": "総合コメント"
    }
    出力は、tasting_stateというキーで返してください。
    """,
    tools=[analyze_tasting],
    output_key="tasting_state",
)
