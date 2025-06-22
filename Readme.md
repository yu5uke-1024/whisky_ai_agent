# Whisky Multi-Agent System

---

## 概要

Whisky Multi-Agent Systemは、ウイスキーの画像解析・テイスティングノート管理・レコメンド・履歴管理を行うマルチエージェントAIシステムです。Google ADKを活用し、複数のAIエージェントが協調して動作します。CLI・LINE Bot両対応。

---

## 主な機能

- **画像解析**  
  ウイスキーボトルのラベル画像からブランド名・蒸溜所・熟成年数などを自動抽出

- **テイスティングノート管理**  
  香り・味わい・余韻・評価などのテイスティングノートを記録・分析

- **ウイスキー情報・履歴管理**  
  Firestoreを用いたウイスキー情報・テイスティングノート・ユーザー履歴の保存・取得

- **レコメンド・一般質問対応**  
  ユーザー履歴に基づくウイスキーのおすすめや、ウイスキーに関する一般的な質問への回答

- **LINE Bot連携**  
  LINE上で画像送信・テキスト対話が可能

---

## システム構成

```
.
├── main.py                # CLIエントリーポイント
├── line_bot_server.py     # LINE Botサーバー (FastAPI)
├── whisky_agent/
│   ├── agent.py           # ルートエージェント定義
│   ├── models.py          # WhiskyInfo, TastingNote等データモデル
│   ├── storage/
│   │   └── firestore.py   # Firestore連携
│   └── sub_agents/
│       ├── image_agent/   # 画像解析サブエージェント
│       ├── tasting_note_agent/ # テイスティングノートサブエージェント
│       └── recommend_agent/    # レコメンド・一般質問サブエージェント
├── utils.py               # セッション管理・共通関数
├── requirements.txt
└── Dockerfile
```

### エージェント構成

- **root_agent**  
  タスクを自動で振り分けるコーディネーター。  
  サブエージェント：  
  - `image_agent`（画像解析）
  - `tasting_note_agent`（テイスティングノート管理）
  - `recommend_agent`（レコメンド・一般質問）

- **image_agent**  
  画像からウイスキー情報を抽出し、Firestoreに保存

- **tasting_note_agent**  
  テイスティングノートの作成・編集・保存

- **recommend_agent**  
  履歴に基づくおすすめや一般的な質問対応

---

## データモデル

- **WhiskyInfo**  
  ブランド名、熟成年数、蒸溜所、生産国、地域、種類など

- **TastingNote**  
  香り（nose）、味わい（palate）、余韻（finish）、評価（rating）

Firestoreにより、ユーザーごと・ウイスキーごとに情報を永続化。

---

## 必要要件

- Python 3.8+
- Google Cloud Firestore（認証情報が必要）
- LINE Bot利用時はLINE Developersのチャネル設定

### Pythonパッケージ

`requirements.txt` より自動インストール推奨

```
python-dotenv
flask
line-bot-sdk
requests
gunicorn
google-generativeai
google-cloud-firestore
urllib3<2
google-adk==1.3.0
fastapi
uvicorn[standard]
python-multipart
```

---

## セットアップ

1. 仮想環境の作成・有効化
    ```bash
    python -m venv venv
    source venv/bin/activate  # Unix系
    venv\Scripts\activate     # Windows
    ```

2. 依存パッケージのインストール
    ```bash
    pip install -r requirements.txt
    ```

3. 環境変数の設定
    - `.env` ファイルを作成し、以下を記載
        ```
        GOOGLE_API_KEY=xxx
        FIREBASE_CREDENTIALS=xxx.json
        LINE_CHANNEL_ACCESS_TOKEN=xxx
        LINE_CHANNEL_SECRET=xxx
        ```

---

## 使い方

### CLI版

```bash
python main.py
```
- ユーザーID入力後、プロンプトに従いテキスト・画像パスを入力
- `exit` または `quit` で終了

### LINE Bot版

```bash
uvicorn line_bot_server:app --host 0.0.0.0 --port 8000
```
- LINE DevelopersでWebhook URLを設定
- 画像・テキストをLINEで送信して利用

---

## Firestore構成

- `users/{user_id}/whisky_collection/{whisky_id}`  
  → ウイスキー情報・テイスティングノート
- `user_sessions/{user_id}`  
  → セッション・会話履歴

---

## 開発・テスト

- 主要ロジックは `whisky_agent/` 配下
- テスト画像は `test_images/` に配置
- Dockerfile/Cloud Build対応

---
