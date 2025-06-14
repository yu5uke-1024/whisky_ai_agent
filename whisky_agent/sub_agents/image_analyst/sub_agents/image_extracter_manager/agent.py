from google.adk.agents import Agent, SequentialAgent, LlmAgent
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError
from .prompts import IMAGE_EXTRACTER_INSTRUCTION
from .....models import WhiskyInfo
from .....models import create_whisky_id


image_extracter_to_user = Agent(
    name="image_extracter_to_user",
    model="gemini-2.0-flash",
    description="文章整形エージェント",
    instruction="""ImageAnalysisをユーザーにわかりやすく文章にして回答してください。
    下記の解答例を参考にしてください。

    **解答例**
    このウイスキーの情報は以下の通りです。
    銘柄: アードベック10年 (例)
    蒸溜所: アードベック蒸溜所 (例)
    生産国: スコットランド (例)
    生産地域: アイラ島 (例)
    ウイスキーの種類: シングルモルトウイスキー (例)
    特徴的な情報: 非常にスモーキー (例)
    この情報を修正・保存しますか？
    """,
)

image_extracter = Agent(
    name="image_extracter",
    model="gemini-2.0-flash",
    description="ウイスキーのラベル画像から新規に情報を抽出する専門家",
    instruction=IMAGE_EXTRACTER_INSTRUCTION,
    output_schema=WhiskyInfo,
    output_key="whisky_info",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    before_agent_callback=create_whisky_id
    )



image_extracter_manager = SequentialAgent(
    name="image_extracter_manager",
    description="ウイスキーのラベル画像から情報を抽出し、ユーザーに文章にして回答する",
    sub_agents=[image_extracter, image_extracter_to_user],
)
