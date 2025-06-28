# ウイスキー・マルチエージェントシステム

---

## 概要

**ウイスキー・マルチエージェントシステム**は、ウイスキー愛好家・コレクター・プロフェッショナル向けのAIプラットフォームです。画像解析、テイスティングノート管理、パーソナライズ推薦、履歴分析などを、Google ADKを活用したマルチエージェント構成で実現します。CLI・LINE Bot両対応、Google Cloud Firestoreによるデータ永続化も特徴です。

---

## 主な特徴

- **画像解析**：ウイスキーボトルのラベル画像からブランド名・蒸溜所・熟成年数などを自動抽出
- **テイスティングノート管理**：香り・味わい・余韻・評価などのノートを記録・編集・分析
- **パーソナライズ推薦**：ユーザー履歴や好みに基づくウイスキーのおすすめ
- **履歴分析**：国・地域ごとの傾向やコレクションの可視化
- **ニュース・Web検索**：ウイスキー関連ニュースや一般的な質問への回答
- **LINE Bot連携**：LINE上でテキスト・画像による対話が可能
- **Firestore連携**：全データを安全かつスケーラブルに保存
- **拡張性の高いマルチエージェント設計**：新たなエージェント追加も容易

---

## システム構成

```
.
├── main.py                # CLIエントリーポイント
├── line_bot_server.py     # LINE Botサーバー (FastAPI)
├── whisky_agent/
│   ├── agent.py           # ルートエージェント（全体の司令塔）
│   ├── models.py          # データモデル（WhiskyInfo, TastingNote等）
│   ├── storage/
│   │   └── firestore.py   # Firestore連携
│   └── sub_agents/
│       ├── image_agent/   # 画像解析エージェント
│       ├── tasting_note_agent/ # テイスティングノートエージェント
│       ├── recommend_agent/    # レコメンドエージェント
│       ├── look_back_agent/       # 履歴分析エージェント
│       └── news_agent/         # ニュース・Web検索エージェント
├── utils.py               # セッション管理・共通関数
├── requirements.txt
└── Dockerfile
```

### エージェント構成

- **ルートエージェント**（whisky_master_agent）
  - ユーザー入力やセッション状態に応じて各サブエージェントへタスクを振り分け
  - サブエージェント：
    - `image_agent`：画像解析・Firestore保存
    - `tasting_note_agent`：テイスティングノート作成・編集・保存
    - `recommend_agent`：パーソナライズ推薦・一般質問
    - `look_back_agent`：履歴分析（国別・傾向分析など）
    - `news_agent`：ウイスキーニュース・Web検索

- **サブエージェント**
  - 各分野ごとに独立したロジック・ツールを持ち、拡張も容易

---

## データモデル

- **WhiskyInfo（ウイスキー情報）**
  - ブランド名（brand）
  - 熟成年数（age）
  - 蒸溜所（distillery）
  - 生産国（country）
  - 地域（region）
  - 種類（whisky_type）

- **TastingNote（テイスティングノート）**
  - 香り（nose）：特徴語リスト
  - 味わい（palate）：特徴語リスト
  - 余韻（finish）：特徴語リスト
  - 評価（rating）：1〜5の数値

Firestoreにより、ユーザー・ウイスキー・セッションごとに情報を永続化します。

---

## 必要要件

- Python 3.8以上
- Google Cloud Firestore（認証情報必須）
- LINE Developersアカウント（LINE Bot利用時）

### 主なPythonパッケージ

- google-adk==1.3.0
- fastapi, uvicorn[standard]
- line-bot-sdk
- google-cloud-firestore
- google-generativeai
- langchain_community, tavily-python
- python-dotenv, requests, gunicorn, python-multipart

`requirements.txt`に全依存パッケージを記載しています。

---

## セットアップ手順

1. **仮想環境の作成・有効化**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Unix系
    venv\Scripts\activate     # Windows
    ```

2. **依存パッケージのインストール**
    ```bash
    pip install -r requirements.txt
    ```

3. **環境変数の設定**
    - `.env`ファイルを作成し、以下を記載
      ```
      GOOGLE_API_KEY=xxx
      FIREBASE_CREDENTIALS=xxx.json
      LINE_CHANNEL_ACCESS_TOKEN=xxx
      LINE_CHANNEL_SECRET=xxx
      ```

4. **（任意）Dockerによるビルド・実行**
    ```bash
    docker build -t whisky-multi-agent .
    docker run -p 8080:8080 whisky-multi-agent
    ```

---

## 使い方

### CLI版

```bash
python main.py
```
- ユーザーIDを入力し、プロンプトに従ってテキストや画像パスを入力
- `exit` または `quit` で終了

### LINE Bot版

```bash
uvicorn line_bot_server:app --host 0.0.0.0 --port 8000
```
- LINE DevelopersでWebhook URLを設定
- LINEでテキストや画像を送信して利用

---

## Firestore構成

- `users/{user_id}/whisky_collection/{whisky_id}`：ウイスキー情報・テイスティングノート
- `user_sessions/{user_id}`：セッション・会話履歴

---

## 各エージェントの詳細

### image_agent（画像解析エージェント）
- ラベル画像からウイスキー情報を抽出
- Firestoreへ自動保存

### tasting_note_agent（テイスティングノートエージェント）
- テイスティングノートの作成・編集・保存
- 構造化ノートの自動生成やウイスキー情報との紐付け

### recommend_agent（レコメンドエージェント）
- 履歴分析によるパーソナライズ推薦
- 他ユーザーの公開履歴も活用した協調フィルタリング
- 一般的なウイスキー質問への回答

### look_back_agent（履歴分析エージェント）
- ユーザー履歴の国別・地域別集計や傾向分析
- コレクションの可視化や発見に活用

### news_agent（ニュース・Web検索エージェント）
- ウイスキー関連ニュースの取得やWeb検索
- Tavily等の外部検索APIとも連携

---

## 開発・拡張ガイド

- 主要ロジックは`whisky_agent/`配下に集約
- 各エージェントは独立・モジュール化されており、追加・差し替えも容易
- 新規サブエージェントは`sub_agents/`配下にディレクトリを作成し、`agent.py`で登録
- テスト画像は`test_images/`に配置可能
- Docker/Cloud Buildによるデプロイにも対応

---

## ライセンス

MITライセンス

---

## 謝辞

- [Google ADK](https://github.com/google/adk)・[Gemini](https://ai.google.dev/)を活用
- [LINE Messaging API](https://developers.line.biz/ja/docs/messaging-api/)利用
- Firestoreによるクラウドデータ管理

---

## お問い合わせ

ご質問・ご要望・コントリビューションはIssue作成または管理者までご連絡ください。
