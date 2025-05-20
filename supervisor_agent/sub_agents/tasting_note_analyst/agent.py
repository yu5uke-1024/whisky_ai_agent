from google.adk.agents import Agent
from google.adk.tools import google_search

tasting_note_analyst = Agent(
    name="tasting_note_analyst",
    model="gemini-2.0-flash-lite",
    description="Whisky tasting note analyst agent",
    instruction="""
    あなたは、ウイスキーのテイスティングノート（香り・味・余韻など）を調べて、ユーザーにわかりやすく伝えるアシスタントです。

    ユーザーから特定のウイスキー銘柄のテイスティングノートについて尋ねられた場合は、google_searchツールを使ってそのウイスキーの香りや味の特徴に関する情報を検索してください。

    可能であれば、香り（nose）、味（palate）、余韻（finish）などの要素に分けて要約してください。

    該当する情報が見つからない場合は、その旨を丁寧に伝えてください。
    """,
    tools=[google_search],
)
