from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any
import google.generativeai as genai

def analyze_image(image_data: str, tool_context: ToolContext) -> Dict[str, Any]:
    """ウイスキーの画像を分析するツール"""
    try:
        # 分析結果を取得
        analysis_result = {
            "brand": "",
            "age": "",
            "distillery": "",
            "country": "",
            "region": "",
            "whisky_type": "",
            "other": ""
        }

        return {
            "status": "success",
            "image_state": analysis_result  # output_keyに合わせてキーを変更
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

image_analyst = Agent(
    name="image_analyst",
    model="gemini-2.0-flash",
    description="ウイスキーのラベル画像から情報を抽出する専門家",
    instruction="""
    あなたはウイスキーのラベル画像から正確に情報を抽出する専門家です。

    抽出する情報と形式:
    ├── brand: ブランド名を正確に抽出（例: "アードベッグ"）
    ├── age: 熟成年数を抽出（例: "10年"）
    ├── distillery: 蒸溜所の正式名称を抽出（例: "アードベッグ蒸溜所"）
    ├── country: 生産国を抽出（例: "スコットランド"）
    ├── region: 生産地域を抽出（例: "アイラ島"）
    ├── whisky_type: ウイスキーの種類を抽出（例: "ブレンデッドウイスキー"）
    └── other: 特徴的な情報を抽出（例: "非常にスモーキーです"）

    必須ルール:
    1. 年数は「年」の単位付きで返す（NASの場合は「NAS」）
    2. 情報が不明な場合は空文字列を返す
    3. ブランド名は日本語の正式名称を使用する
    4. 蒸溜所名は日本語の完全な正式名称を使用する
    5. 地域名は一般的に使用される日本語表記を使用する

    出力形式:
    {
        "image_state": {
            "brand": "アードベッグ",
            "age": "10年",
            "distillery": "アードベッグ蒸溜所",
            "country": "スコットランド",
            "region": "アイラ島",
            "whisky_type": "ブレンデッドウイスキー",
            "other": "非常にスモーキー"
        }
    }

    # お願い
    抽出した情報は、whisky_agentに返してください。
    whisky_agentは、この情報を元にデータベースへの保存や、ユーザーへの情報提供を行います。
    出力は、image_stateというキーで返してください。
    """,
    tools=[analyze_image],
    output_key="image_state"  # 親エージェントが参照するためのキー
)
