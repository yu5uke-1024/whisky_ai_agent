from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from typing import Dict, Any
from pydantic import BaseModel, Field
from .sub_agents.image_extracter import image_extracter
from .sub_agents.image_modifier import image_modifier
from .prompts import IMAGE_ANALYST_INSTRUCTION

image_analyst = Agent(
    name="image_analyst",
    model="gemini-2.5-flash-preview-05-20",
    description="ウイスキーのラベル画像から情報を抽出する専門家",
    instruction=IMAGE_ANALYST_INSTRUCTION,
    sub_agents=[image_extracter],
    tools=[
        AgentTool(image_modifier)
    ]
)
