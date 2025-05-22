# Whisky Multi-Agent System

ウイスキーの画像解析とテイスティングノート管理のためのマルチエージェントシステム。Google ADKを活用し、複数のAIエージェントが協調して動作します。

## 機能

- 🔍 **画像解析**: ウイスキーボトルの画像から情報を自動抽出
  - ブランド名
  - 蒸溜所
  - 熟成年数
  - アルコール度数
  - その他の特徴

- 📝 **テイスティングノート**: ウイスキーの味わいを詳細に分析
  - 香り (Nose)
  - 味わい (Palate)
  - 余韻 (Finish)
  - 総合評価

- 💾 **データ管理**
  - ウイスキー情報の保存
  - テイスティングノートの記録
  - 履歴の閲覧

- ❓ **一般的な質問対応**
  - ウイスキーの基礎知識
  - 製法や特徴の説明
  - 用語解説

## システム構成

### メインエージェント
- `root_agent`: 全体のコーディネーターとして機能

### サブエージェント
1. `image_analyst`: 画像解析専門
2. `tasting_note_analyst`: テイスティング分析専門

### データモデル
- `WhiskyInfo`: ウイスキー情報の管理
- `TastingNote`: テイスティングノートの管理

## 必要要件

```bash
# 必要なPythonパッケージ
python-dotenv
flask
line-bot-sdk
requests
gunicorn
google-generativeai
google-cloud-firestore
urllib3<2
google-adk
```

## セットアップ

1. 環境のセットアップ
```bash
# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Unix系
venv\Scripts\activate     # Windows

# 依存パッケージのインストール
pip install -r requirements.txt
```

2. 環境変数の設定
```bash
# .envファイルを作成し、必要な環境変数を設定
touch .env
```

必要な環境変数:
- `GOOGLE_API_KEY`: Google APIキー（Gemini APIアクセス用）
- `FIREBASE_CREDENTIALS`: Firestore認証情報（オプション）

## 使用方法

1. アプリケーションの起動
```bash
python main.py
```

2. 対話の開始
- プロンプトが表示されたら、以下のような操作が可能：
  - 画像の解析
  - テイスティングノートの作成
  - 一般的な質問
  - 履歴の確認

3. 終了
```bash
exit
```
または
```bash
quit
```

## プロジェクト構造
