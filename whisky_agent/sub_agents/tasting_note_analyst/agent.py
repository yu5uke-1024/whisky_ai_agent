from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field, ValidationError
from ...storage.firestore import FirestoreClient # FirestoreClientをインポート
from .sub_agents.tasting_note_creator import tasting_note_creator
from .sub_agents.tasting_note_modifier import tasting_note_modifier
from .prompts import TASTING_NOTE_ANALYST_INSTRUCTION

# Firestoreクライアントのインスタンスを作成
firestore_client = FirestoreClient()


tasting_note_analyst = Agent(
    name="tasting_note_analyst",
    model="gemini-2.5-flash-preview-05-20",
    description="ウイスキーのテイスティングノートを管理・分析するエージェント",
    instruction=TASTING_NOTE_ANALYST_INSTRUCTION,
    tools=[
        AgentTool(tasting_note_creator),
        AgentTool(tasting_note_modifier)
    ])
