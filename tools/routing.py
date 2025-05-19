from google.adk.tools import FunctionTool

def route_to_vision(image_b64: str, tool_context):
    tool_context.actions.transfer_to_agent = "vision_agent"
    return {"status": "transferred"}

route_to_vision_tool = FunctionTool(
    func=route_to_vision,
)
