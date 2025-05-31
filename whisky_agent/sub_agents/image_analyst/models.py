from pydantic import BaseModel, Field

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
