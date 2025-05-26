from google.adk.agents import Agent
from typing import Dict, Any
from pydantic import BaseModel, Field

# --- Define Output Schema ---
class ImageAnalysis(BaseModel):
    brand: str = Field(
        description="ブランド名（日本語の正式名称）",
        default=""
    )
    age: str = Field(
        description="熟成年数（年の単位付き、NASの場合は「NAS」）",
        default=""
    )
    distillery: str = Field(
        description="蒸溜所の正式名称（日本語）",
        default=""
    )
    country: str = Field(
        description="生産国",
        default=""
    )
    region: str = Field(
        description="生産地域",
        default=""
    )
    whisky_type: str = Field(
        description="ウイスキーの種類",
        default=""
    )
    other: str = Field(
        description="その他の特徴的な情報",
        default=""
    )

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

    応答形式:
    {
        "brand": "アードベッグ",
        "age": "10年",
        "distillery": "アードベッグ蒸溜所",
        "country": "スコットランド",
        "region": "アイラ島",
        "whisky_type": "シングルモルトウイスキー",
        "other": "非常にスモーキー"
    }
    """,
    output_schema=ImageAnalysis,
    output_key="image_analysis"
)
