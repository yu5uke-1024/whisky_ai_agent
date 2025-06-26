from typing import Optional
from google.adk.agents import Agent
from .sub_agents.image_agent import image_agent
from .sub_agents.tasting_note_agent import tasting_note_agent
from .sub_agents.recommend_agent import recommend_agent
from .sub_agents.news_agent import news_agent
from .prompts import INSTRUCTION
from google.adk.agents.callback_context import CallbackContext
from google.genai import types # For types.Content


def check_if_agent_should_run(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Logs entry and checks 'skip_llm_agent' in session state.
    If True, returns Content to skip the agent's execution.
    If False or not present, returns None to allow execution.
    """
    agent_name = callback_context.agent_name

    user_id = callback_context.state.get("user_id", 'default_user_id')
    callback_context.state["user_id"] = user_id

    return None


# ルートエージェントの定義
root_agent = Agent(
    name="whisky_master_agent",
    model="gemini-2.5-flash",
    description="ウイスキー関連タスクの振り分け専門エージェント。自らは回答せず、対話履歴を確認して適切なサブエージェントにタスクを委譲します。",
    instruction=INSTRUCTION, # エージェントの指示プロンプト
    sub_agents=[
        image_agent, # 画像解析サブエージェント
        tasting_note_agent, # テイスティングノート分析サブエージェント
        recommend_agent, # おすすめエージェント
        news_agent
    ],
    before_agent_callback=check_if_agent_should_run # Assign the callback
)
