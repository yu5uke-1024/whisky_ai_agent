from google.adk.agents import Agent
from .prompts import TASTING_NOTE_CREATION_INSTRUCTION
from .....models import TastingAnalysis


tasting_note_creator = Agent(
    name="tasting_note_creator",
    model="gemini-2.5-flash",
    description="ウイスキーのテイスティングノート作成の専門家。提供されたウイスキー情報に基づいてノートを生成します。",
    instruction=TASTING_NOTE_CREATION_INSTRUCTION,
    output_schema=TastingAnalysis,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_key="tasting_note",
)
