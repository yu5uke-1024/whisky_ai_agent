from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any, List, Union
from ...models import TastingAnalysis

def modify_nose(nose: Union[str, List[str]], tool_context: ToolContext) -> dict:
    """香りの特徴を修正する

    Args:
        nose: 新しい香りの特徴（文字列または文字列のリスト）
        tool_context: セッション状態にアクセスするためのコンテキスト

    Returns:
        修正結果のメッセージ
    """
    print(f"--- Tool: modify_nose called with '{nose}' ---")

    current_note = tool_context.state.get("current_tasting_note", TastingAnalysis())
    current_note.nose = [nose] if isinstance(nose, str) else nose
    tool_context.state["current_tasting_note"] = current_note

    return {
        "action": "modify_nose",
        "nose": nose,
        "message": f"Updated nose characteristics to: {nose}"
    }

def modify_palate(palate: Union[str, List[str]], tool_context: ToolContext) -> dict:
    """味わいの特徴を修正する"""
    print(f"--- Tool: modify_palate called with '{palate}' ---")

    current_note = tool_context.state.get("current_tasting_note", TastingAnalysis())
    current_note.palate = [palate] if isinstance(palate, str) else palate
    tool_context.state["current_tasting_note"] = current_note

    return {
        "action": "modify_palate",
        "palate": palate,
        "message": f"Updated palate characteristics to: {palate}"
    }

def modify_finish(finish: Union[str, List[str]], tool_context: ToolContext) -> dict:
    """余韻の特徴を修正する"""
    print(f"--- Tool: modify_finish called with '{finish}' ---")

    current_note = tool_context.state.get("current_tasting_note", TastingAnalysis())
    current_note.finish = [finish] if isinstance(finish, str) else finish
    tool_context.state["current_tasting_note"] = current_note

    return {
        "action": "modify_finish",
        "finish": finish,
        "message": f"Updated finish characteristics to: {finish}"
    }

def modify_rating(rating: float, tool_context: ToolContext) -> dict:
    """評価を修正する"""
    print(f"--- Tool: modify_rating called with {rating} ---")

    if not (1.0 <= rating <= 5.0):
        return {
            "action": "modify_rating",
            "status": "error",
            "message": "Rating must be between 1.0 and 5.0"
        }

    current_note = tool_context.state.get("current_tasting_note", TastingAnalysis())
    current_note.rating = rating
    tool_context.state["current_tasting_note"] = current_note

    return {
        "action": "modify_rating",
        "rating": rating,
        "message": f"Updated rating to: {rating}"
    }

def view_tasting_note(tool_context: ToolContext) -> dict:
    """現在のテイスティングノートを表示する"""
    print("--- Tool: view_tasting_note called ---")

    note = tool_context.state.get("current_tasting_note", TastingAnalysis())

    return {
        "action": "view_tasting_note",
        "note": note.dict(),
        "message": f"""Current tasting note:
        Nose: {', '.join(note.nose)}
        Palate: {', '.join(note.palate)}
        Finish: {', '.join(note.finish)}
        Rating: {note.rating}"""
    }

tasting_note_modifier = Agent(
    name="tasting_note_modifier",
    model="gemini-2.0-flash-lite",
    description="ウイスキーのテイスティングノート修正の専門家",
    instruction="""
    あなたはウイスキーのテイスティングノートを修正する専門家です。

    テイスティングノートの情報は状態として保存されています：
    - 香り (Nose)
    - 味わい (Palate)
    - 余韻 (Finish)
    - 評価 (Rating)

    以下の機能を使用してテイスティングノートを修正できます：
    1. 香りの修正 (modify_nose)
    2. 味わいの修正 (modify_palate)
    3. 余韻の修正 (modify_finish)
    4. 評価の修正 (modify_rating)
    5. 現在のノートの表示 (view_tasting_note)

    **修正のガイドライン:**

    1. 各特徴（香り、味わい、余韻）の修正:
       - 単一の特徴または特徴のリストとして指定可能
       - 例: "バニラ" または ["バニラ", "スパイシー"]

    2. 評価の修正:
       - 1.0から5.0の範囲で指定（0.5刻み）
       - 範囲外の値は受け付けない

    3. 表示:
       - view_tasting_noteを使用して現在のノートを確認
       - 修正前後で内容を確認することを推奨

    常に専門的な観点から適切な修正を行い、
    修正後は変更内容を明確に説明してください。
    """,
    tools=[
        modify_nose,
        modify_palate,
        modify_finish,
        modify_rating,
        view_tasting_note,
    ]
)
