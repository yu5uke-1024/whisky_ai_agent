from google.adk.agents import Agent, SequentialAgent, LlmAgent
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError
from .prompts import IMAGE_EXTRACTER_INSTRUCTION
from .....models import WhiskyInfo
from .....models import create_whisky_id

output_reviser = Agent(
    name="output_reviser",
    model="gemini-2.5-flash",
    description="文章整形エージェント",
    instruction="""ImageAnalysisをユーザーにわかりやすく文章にして回答してください。
    下記の解答例を参考にしてください。

    **解答例**
    こちらがウイスキーの情報です。
    銘柄: アードベック/響 (例)
    熟成年数: 10年/ノンエイジ (例)
    蒸溜所: アードベック蒸溜所/未明 (例)
    生産国: スコットランド/日本 (例)
    生産地域: アイラ島/未明 (例)
    ウイスキーの種類: シングルモルト/ブレンデッド (例)
    この情報を修正・保存しますか？
    """,
)

image_extracter = Agent(
    name="image_extracter",
    instruction=IMAGE_EXTRACTER_INSTRUCTION,
    output_schema=WhiskyInfo,
    output_key="whisky_info",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    before_agent_callback=create_whisky_id
    )


whisky_label_processor = SequentialAgent(
    name="whisky_label_processor",
    description="ウイスキーのラベル画像から情報を抽出し、ユーザーに文章にして回答する",
    sub_agents=[image_extracter, output_reviser],
)
