from google.adk.tools import FunctionTool


def ocr_tool(image_b64: str) -> dict:
  return "アードベックです。"


ocr_tool = FunctionTool(func=ocr_tool)
