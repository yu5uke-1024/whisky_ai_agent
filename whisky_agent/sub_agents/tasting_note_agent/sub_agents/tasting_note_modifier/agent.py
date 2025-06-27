from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from typing import Literal

NoteTypeStr = Literal["nose", "palate", "finish"]

def modify_rating(rating: float, tool_context: ToolContext) -> dict:
    """評価を修正する

    Args:
        rating: 評価値（1.0から5.0の範囲の浮動小数点数）
        tool_context: セッションステートにアクセスするためのコンテキスト

    Returns:
        更新結果の確認メッセージを含む辞書
        {
            "action": "modify_rating",
            "rating": float,
            "message": str
        }

    Raises:
        ValueError: ratingが1.0から5.0の範囲外の場合
    """
    print(f"--- Tool: modify_rating called with {rating} ---")

    if not (1.0 <= rating <= 5.0):
        return {
            "action": "modify_rating",
            "status": "error",
            "message": "Rating must be between 1.0 and 5.0"
        }

    # ステートの完全なコピーを作成
    updated_tasting_note = dict(tool_context.state["tasting_note"])
    updated_tasting_note["rating"] = rating

    # 新しいステートで更新
    tool_context.state["tasting_note"] = updated_tasting_note

    return {
        "action": "modify_rating",
        "rating": rating,
        "message": f"Updated rating to: {rating}"
    }


def view_tasting_note(tool_context: ToolContext) -> dict:
    """現在のテイスティングノートを表示する

    Args:
        tool_context: セッションステートにアクセスするためのコンテキスト

    Returns:
        現在のテイスティングノートの内容
    """
    print("--- Tool: view_tasting_note called ---")

    tasting_note = tool_context.state.get("tasting_note", {})

    return {
        "action": "view_tasting_note",
        "tasting_note": tasting_note,
        "message": f"""
    香り: {', '.join(tasting_note.get('nose', []))}
    味わい: {', '.join(tasting_note.get('palate', []))}
    余韻: {', '.join(tasting_note.get('finish', []))}
    評価: {tasting_note.get('rating', 0.0)}
    """
        }

def add_note_characteristic(
    note_type: NoteTypeStr,
    characteristic: str,
    tool_context: ToolContext
) -> dict:
    """テイスティングノートの特徴を追加する

    Args:
        note_type: 特徴の種類（"nose"/"palate"/"finish"のいずれか）
        characteristic: 追加する特徴
        tool_context: セッションステートにアクセスするためのコンテキスト

    Returns:
        更新結果の確認メッセージを含む辞書
    """
    print(f"--- Tool: add_note_characteristic called for {note_type} with '{characteristic}' ---")

    if note_type not in ["nose", "palate", "finish"]:
        return {
            "action": "add_note_characteristic",
            "status": "error",
            "message": f"Invalid note type: {note_type}. Must be one of: nose, palate, finish"
        }

    # ステートの完全なコピーを作成
    updated_tasting_note = dict(tool_context.state["tasting_note"])

    # 現在の特徴リストを取得し、新しい特徴を追加
    current_notes = updated_tasting_note.get(note_type, [])
    if characteristic not in current_notes:  # 重複を防ぐ
        current_notes.append(characteristic)
        updated_tasting_note[note_type] = current_notes

        # 新しいステートで更新
        tool_context.state["tasting_note"] = updated_tasting_note

        return {
            "action": "add_note_characteristic",
            "note_type": note_type,
            "characteristic": characteristic,
            "message": f"Added '{characteristic}' to {note_type} characteristics"
        }
    else:
        return {
            "action": "add_note_characteristic",
            "status": "error",
            "message": f"'{characteristic}' is already in {note_type} characteristics"
        }

def remove_note_characteristic(
    note_type: NoteTypeStr,
    characteristic: str,
    tool_context: ToolContext
) -> dict:
    """テイスティングノートの特徴を削除する

    Args:
        note_type: 特徴の種類（"nose"/"palate"/"finish"のいずれか）
        characteristic: 削除する特徴
        tool_context: セッションステートにアクセスするためのコンテキスト

    Returns:
        更新結果の確認メッセージを含む辞書
    """
    print(f"--- Tool: remove_note_characteristic called for {note_type} with '{characteristic}' ---")

    if note_type not in ["nose", "palate", "finish"]:
        return {
            "action": "remove_note_characteristic",
            "status": "error",
            "message": f"Invalid note type: {note_type}. Must be one of: nose, palate, finish"
        }

    # ステートの完全なコピーを作成
    updated_tasting_note = dict(tool_context.state["tasting_note"])

    # 現在の特徴リストを取得
    current_notes = updated_tasting_note.get(note_type, [])

    if characteristic in current_notes:
        current_notes.remove(characteristic)
        updated_tasting_note[note_type] = current_notes

        # 新しいステートで更新
        tool_context.state["tasting_note"] = updated_tasting_note

        return {
            "action": "remove_note_characteristic",
            "note_type": note_type,
            "characteristic": characteristic,
            "message": f"Removed '{characteristic}' from {note_type} characteristics"
        }
    else:
        return {
            "action": "remove_note_characteristic",
            "status": "error",
            "message": f"'{characteristic}' not found in {note_type} characteristics"
        }

def update_note_characteristic(
    note_type: NoteTypeStr,
    old_characteristic: str,
    new_characteristic: str,
    tool_context: ToolContext
) -> dict:
    """テイスティングノートの特徴を変更する

    Args:
        note_type: 特徴の種類（"nose"/"palate"/"finish"のいずれか）
        old_characteristic: 変更前の特徴
        new_characteristic: 変更後の特徴
        tool_context: セッションステートにアクセスするためのコンテキスト

    Returns:
        更新結果の確認メッセージを含む辞書
    """
    print(f"--- Tool: update_note_characteristic called for {note_type}: '{old_characteristic}' -> '{new_characteristic}' ---")

    if note_type not in ["nose", "palate", "finish"]:
        return {
            "action": "update_note_characteristic",
            "status": "error",
            "message": f"Invalid note type: {note_type}. Must be one of: nose, palate, finish"
        }

    # ステートの完全なコピーを作成
    updated_tasting_note = dict(tool_context.state["tasting_note"])

    # 現在の特徴リストを取得
    current_notes = updated_tasting_note.get(note_type, [])

    if old_characteristic in current_notes:
        # インデックスを取得して更新
        index = current_notes.index(old_characteristic)
        current_notes[index] = new_characteristic
        updated_tasting_note[note_type] = current_notes

        # 新しいステートで更新
        tool_context.state["tasting_note"] = updated_tasting_note

        return {
            "action": "update_note_characteristic",
            "note_type": note_type,
            "old_characteristic": old_characteristic,
            "new_characteristic": new_characteristic,
            "message": f"Updated {note_type} characteristic from '{old_characteristic}' to '{new_characteristic}'"
        }
    else:
        return {
            "action": "update_note_characteristic",
            "status": "error",
            "message": f"'{old_characteristic}' not found in {note_type} characteristics"
        }

tasting_note_modifier = Agent(
    name="tasting_note_modifier",
    model="gemini-2.5-flash",
    description="ウイスキーのテイスティングノート修正の専門家",
    instruction="""
    あなたはウイスキーのテイスティングノートを修正する専門家です。
    ユーザーの要望に応じて、既存のテイスティングノートを適切に修正します。

    【テイスティングノートの構成】
    テイスティングノートは以下の4つの要素で構成されています
    1. 香り (Nose) - ウイスキーから感じられる香りの特徴
    2. 味わい (Palate) - 口に含んだ時の味わいの特徴
    3. 余韻 (Finish) - 飲み込んだ後に残る余韻の特徴
    4. 評価 (Rating) - 総合的な評価（1.0-5.0）

    【修正可能な項目と入力形式】
    1. 香り・味わい・余韻の特徴:
       - 文字列または文字列のリストで指定
       - 例: "バニラ" または ["バニラ", "スパイシー", "フルーティー"]
       - 具体的で専門的な表現を使用

    2. 評価:
       - 1.0から5.0の範囲で指定（0.5刻み）
       - 例: 3.5, 4.0, 4.5
       - 範囲外の値は受け付けません

    【使用可能なツール】
    1. modify_nose: 香りの特徴を修正
    2. modify_palate: 味わいの特徴を修正
    3. modify_finish: 余韻の特徴を修正
    4. modify_rating: 評価を修正
    5. view_tasting_note: 現在のテイスティングノートを表示

    【修正プロセス】
    1. まず view_tasting_note で現在の内容を確認
    2. 必要な修正を実行
    3. 再度 view_tasting_note で香り・味わい・余韻・評価の全ての情報を確認
    4. 修正部分だけではなく、香り・味わい・余韻・評価の全てを連携して説明

    【注意事項】
    - 常にウイスキーの専門家としての視点を保持
    - 具体的で正確な表現を使用
    - 修正前後の変更点を明確に説明
    - 一貫性のある評価を心がける
    """,
    tools=[
        view_tasting_note,
        modify_rating,
        add_note_characteristic,
        remove_note_characteristic,
        update_note_characteristic,
    ]
)
