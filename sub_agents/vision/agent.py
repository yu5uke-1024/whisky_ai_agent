from google.adk.agents import Agent
from .tools.ocr import ocr_tool

vision_agent = Agent(
    name="vision_agent",
    model="gemini-1.5-flash",      # 軽量モデルで十分
    instruction="受け取った画像を ocr_tool で処理し結果をそのまま返答してください。",
    tools=[ocr_tool],
)
