from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field, ValidationError
from ...storage.firestore import FirestoreClient # FirestoreClientをインポート
from .sub_agents.tasting_note_creator import tasting_note_creator
from .sub_agents.tasting_note_modifier import tasting_note_modifier

# Firestoreクライアントのインスタンスを作成
firestore_client = FirestoreClient()


tasting_note_analyst = Agent(
    name="tasting_note_analyst",
    model="gemini-2.0-flash",
    description="ウイスキーのテイスティングノートを管理・分析するエージェント",
    instruction="""
    あなたはウイスキーのテイスティングノートの専門家です。
    ユーザーからの指示に基づき、テイスティングノートの「生成」と「修正」を行います。

    - 新規作成の場合は、tasting_note_creatorエージェントを使用します。
    - 既存ノートの修正の場合は、tasting_note_modifierエージェントを使用します。

    最後に、テイスティングノートの内容を文章に直して、わかりやすくユーザーに提示してください。

    例:
    このウイスキーは、フルーツのような香りが強いです。
    味わいは、フルーツのような味わいが強く、余韻は、フルーツのような余韻が強い。
    評価は4.5です。
    """,
    tools=[
        AgentTool(tasting_note_creator),
        AgentTool(tasting_note_modifier)
    ])
