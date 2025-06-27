from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from typing import Literal
from .prompts import IMAGE_MODIFICATION_INSTRUCTION
from pydantic import Field

# 修正可能なフィールドの型定義
FieldType = Literal["brand", "age", "distillery", "country", "region", "whisky_type"]


def view_image_info(tool_context: ToolContext) -> dict:
    """現在の画像情報を表示する

    Args:
        tool_context: セッションステートにアクセスするためのコンテキスト

    Returns:
        現在の画像情報の内容
    """
    print("--- Tool: view_image_info called ---")

    whisky_info = tool_context.state.get("whisky_info", {})

    return {
        "action": "view_image_info",
        "whisky_info": whisky_info,
        "message": f"""
    銘柄名: {whisky_info.get('brand', '')}
    熟成年数: {whisky_info.get('age', '')}
    蒸溜所: {whisky_info.get('distillery', '')}
    生産国: {whisky_info.get('country', '')}
    地域: {whisky_info.get('region', '')}
    種類: {whisky_info.get('whisky_type', '')}
    """
    }

def modify_field(field: FieldType, value: str, tool_context: ToolContext) -> dict:
    """画像情報の指定フィールドを修正する

    Args:
        field: 修正するフィールド名
        value: 新しい値
        tool_context: セッションステートにアクセスするためのコンテキスト

    Returns:
        更新結果の確認メッセージを含む辞書
    """
    print(f"--- Tool: modify_field called for '{field}' with value '{value}' ---")

    # フィールド名の日本語マッピング
    field_names_ja = {
        "brand": "ブランド名",
        "age": "熟成年数",
        "distillery": "蒸溜所名",
        "country": "生産国",
        "region": "生産地域",
        "whisky_type": "ウイスキーの種類",
    }

    # 熟成年数の特別なバリデーション
    if field == "age" and not (value.endswith('年') or value == 'ノンエイジ'):
        return {
            "action": "modify_field",
            "status": "error",
            "message": "熟成年数は「年」の単位付きで指定するか、'ノンエイジ'を指定してください"
        }

    updated_whisky_info = dict(tool_context.state.get("whisky_info", {}))
    updated_whisky_info[field] = value
    tool_context.state["whisky_info"] = updated_whisky_info

    return {
        "action": "modify_field",
        "field": field,
        "value": value,
        "message": f"{field_names_ja[field]}を '{value}' に更新しました"
    }


image_modifier = Agent(
    name="image_modifier",
    model="gemini-2.5-flash",
    description="ウイスキーのラベル画像から抽出した情報を修正する専門家",
    instruction=IMAGE_MODIFICATION_INSTRUCTION,
    tools=[
        view_image_info,
        modify_field,
    ],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True
)
