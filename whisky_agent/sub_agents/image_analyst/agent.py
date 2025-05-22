from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
import google.generativeai as genai
import base64
import json
import re
from typing import Dict, Any

def analyze_whisky_image(image_base64: str, tool_context: ToolContext) -> Dict[str, Any]:
    """ウイスキー画像を解析するツール"""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Base64文字列をそのまま使用するか、バイトデータに変換
        if image_base64.startswith('data:image'):
            # データURLの場合、Base64部分を抽出
            image_base64 = image_base64.split(',')[1]

        prompt_text = """
        このウイスキーの銘柄情報を以下のJSON形式で出力してください。日本語で回答してください。
        情報がわからない場合はWeb検索をして情報を取得してください。

        {
          "brand": "銘柄名",
          "distillery": "蒸留所名",
          "age": "熟成年数",
          "country": "国名",
          "region": "地域",
          "whiskey_type": "ウイスキーのタイプ",
          "alcohol_content": "アルコール度数",
          "cask_type": "カスクタイプ",
          "other": "その他の特徴"
        }
        """

        response = model.generate_content([
            prompt_text,
            {"mime_type": "image/jpeg", "data": image_base64}
        ])

        json_str = re.search(r"\{.*\}", response.text, re.DOTALL)
        if not json_str:
            return {"status": "error", "error": "JSON形式の応答が見つかりません"}

        whiskey_info = json.loads(json_str.group(0))
        formatted_info = {k: whiskey_info.get(k, "不明") for k in [
            "brand", "distillery", "age", "country", "region",
            "whiskey_type", "alcohol_content", "cask_type", "other"
        ]}

        return {
            "status": "success",
            "analysis": formatted_info,
            "formatted_text": format_whisky_info(formatted_info)
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}

def format_whisky_info(info: Dict[str, str]) -> str:
    """解析結果を読みやすい形式に整形"""
    return f"""【銘柄】{info['brand']}
    【蒸留所】{info['distillery']}
    【ウイスキー分類】{info['whiskey_type']}
    【国】{info['country']}
    【地域】{info['region']}
    【熟成年数】{info['age']}
    【アルコール度数】{info['alcohol_content']}
    【カスクタイプ】{info['cask_type']}
    【その他】{info['other']}""".strip()

image_analyst = Agent(
    name="image_analyst",
    model="gemini-2.0-flash-lite",
    description="ウイスキーの画像分析スペシャリスト",
    instruction="""
    あなたはウイスキーの画像分析スペシャリストです。

    主な役割：
    1. ウイスキーの画像からラベル情報を読み取り
    2. ボトルの特徴を分析
    3. 詳細情報の抽出と提供

    応答形式：
    - 構造化された情報を日本語で提供
    - 不明な情報がある場合はその旨を明記
    """,
    tools=[analyze_whisky_image],
)
