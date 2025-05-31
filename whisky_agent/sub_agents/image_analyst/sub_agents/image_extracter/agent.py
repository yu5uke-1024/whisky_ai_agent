from google.adk.agents import Agent
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError
from .prompts import IMAGE_EXTRACTER_INSTRUCTION
from ...models import ImageAnalysis

image_extracter = Agent(
    name="image_extracter",
    model="gemini-2.0-flash",
    description="ウイスキーのラベル画像から新規に情報を抽出する専門家",
    instruction=IMAGE_EXTRACTER_INSTRUCTION,
    output_schema=ImageAnalysis,
    output_key="image_extracter",
)
