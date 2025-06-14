from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field, ValidationError
from ...storage.firestore import FirestoreClient # FirestoreClientをインポート
from .prompts import RECOMMEND_AGENT_INSTRUCTION


recommend_agent = Agent(
    name="recommend_agent",
    model="gemini-2.5-flash-preview-05-20",
    description="ウイスキーのおすすめを提案するエージェント",
    instruction=RECOMMEND_AGENT_INSTRUCTION)
