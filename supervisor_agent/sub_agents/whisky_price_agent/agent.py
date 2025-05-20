from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

# ツール関数：ウイスキーの値段を返す
def get_whisky_price(brand: str, tool_context: ToolContext) -> dict:
    """Return the price of a given whisky brand."""
    print(f"--- Tool: get_whisky_price called for brand: {brand} ---")

    # 仮のウイスキー価格リスト（実装ではAPIやDBと連携可能）
    whisky_prices = {
        "Ardbeg 10": 6000,
        "Lagavulin 16": 12000,
        "Yamazaki 12": 18000,
        "Hakushu": 8500,
        "Laphroaig 10": 7000,
        "Macallan 12": 11000,
        "Bowmore 12": 6500,
        "Nikka From the Barrel": 5000,
        "default": 9999,
    }

    price = whisky_prices.get(brand, whisky_prices["default"])

    # 状態保存（例：最後に問い合わせたウイスキー名）
    tool_context.state["last_whisky_asked"] = brand

    return {"status": "success", "brand": brand, "price": price}

# エージェント定義：whisky_price_agent
whisky_price_agent = Agent(
    name="whisky_price_agent",
    model="gemini-2.0-flash-lite",
    description="An agent that answers whisky price questions.",
    instruction="""
    あなたはウイスキーの価格に関する専門エージェントです。

    ウイスキーの価格を尋ねられた場合は、以下の手順で対応してください：

    1. get_whisky_priceツールを使用して、ブランド名に基づいた価格を取得します。
    2. ブランドが既知のリストに含まれていない場合は、価格がわからない旨のデフォルトメッセージで対応します。
    3. 必ずブランド名と推定価格（日本円）を含めて回答してください。

    例）
    「Ardbeg 10 の推定価格は6,000円です。」

    ウイスキーの価格に関係のない質問をされた場合は、その内容とタスクをマネージャーエージェントに委任してください。
    """,
    tools=[get_whisky_price],
)
