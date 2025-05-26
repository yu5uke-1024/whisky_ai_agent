# Whisky AI Assistant セットアップガイド

このガイドでは、改良されたマルチエージェントシステムをFlutterアプリから起動する方法を説明します。

## 前提条件

### Python環境
- Python 3.8以上
- 必要なパッケージがインストールされていること

### Flutter環境
- Flutter SDK 3.0以上
- Chrome または Edge ブラウザ（Web版実行用）

### 環境変数
- `.env`ファイルに必要なAPI キーが設定されていること
  ```
  GOOGLE_API_KEY=your_google_api_key_here
  ```

## セットアップ手順

### 1. Python依存関係のインストール

```bash
# プロジェクトルートディレクトリで実行
pip install -r requirements.txt
```

### 2. Flutter依存関係のインストール

```bash
# whisky_ai_webディレクトリに移動
cd whisky_ai_web

# Flutter依存関係をインストール
flutter pub get

# プロジェクトルートに戻る
cd ..
```

## 起動方法

### 方法1: APIサーバー経由でFlutterアプリから利用（推奨）

#### ステップ1: PythonのAPIサーバーを起動

```bash
# プロジェクトルートディレクトリで実行
python api_server.py
```

サーバーが正常に起動すると、以下のようなメッセージが表示されます：
```
API Server started with context-aware agent. Session ID: [session_id]
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

#### ステップ2: FlutterアプリをWebで起動

新しいターミナルウィンドウで：

```bash
# whisky_ai_webディレクトリに移動
cd whisky_ai_web

# Flutter Webアプリを起動
flutter run -d chrome
```

または、特定のポートで起動する場合：

```bash
flutter run -d chrome --web-port 3000
```

### 方法2: コマンドラインから直接利用

```bash
# プロジェクトルートディレクトリで実行
python main.py
```

### 方法3: テストスクリプトで動作確認

```bash
# プロジェクトルートディレクトリで実行
python test_conversation_continuity.py
```

## 機能確認

### 会話の連続性テスト

1. Flutterアプリまたはコマンドラインで以下の順序で質問してください：

   1. "こんにちは！ウイスキーについて教えてください。"
   2. "山崎12年について詳しく教えてください。"
   3. "先ほど話した山崎12年のテイスティングノートを作成してください。"
   4. "これまでの会話の履歴を教えてください。"

2. エージェントが過去の会話を参照して適切に回答することを確認してください。

### 画像解析機能テスト（Flutterアプリのみ）

1. ウイスキーボトルの画像をアップロード
2. "この画像のウイスキーを解析してください"と送信
3. image_analystが画像を解析して情報を抽出することを確認

### データ保存・取得テスト

1. "保存されているウイスキー情報を確認してください"と質問
2. セッション内で保存されたデータが表示されることを確認

## トラブルシューティング

### APIサーバーに接続できない場合

1. APIサーバーが起動していることを確認
2. ポート8000が使用可能であることを確認
3. ファイアウォールの設定を確認

### Flutter Webアプリが起動しない場合

1. Flutter SDKが正しくインストールされていることを確認
2. `flutter doctor`コマンドで環境を確認
3. Chrome/Edgeブラウザが利用可能であることを確認

### 環境変数エラーの場合

1. `.env`ファイルがプロジェクトルートに存在することを確認
2. `GOOGLE_API_KEY`が正しく設定されていることを確認

## 改良点

この改良版では以下の問題が修正されています：

1. **会話の連続性**: セッション状態が適切に管理され、過去の会話を参照可能
2. **サブエージェント結果の保存**: image_analystやtasting_note_analystの実行結果がセッションに保存
3. **コンテキスト情報の取得**: `get_context_info`ツールで過去の情報を動的に取得
4. **データの永続化**: ウイスキー情報とテイスティングノートがセッション内で永続化

## ファイル構成

```
whisky_ai_agent/
├── main.py                    # コマンドライン版メインファイル
├── api_server.py             # APIサーバー（改良版）
├── test_conversation_continuity.py  # テストスクリプト
├── utils.py                  # ユーティリティ関数（改良版）
├── whisky_agent/
│   ├── agent.py             # メインエージェント（改良版）
│   ├── sub_agents/          # サブエージェント
│   ├── models/              # データモデル
│   └── storage/             # ストレージ関連
└── whisky_ai_web/           # Flutterアプリ
    ├── lib/main.dart        # Flutterメインファイル（修正版）
    └── ...
```

## 注意事項

- APIサーバーは開発用設定のため、本番環境では適切なセキュリティ設定を行ってください
- 画像ファイルは一時的にローカルに保存されますが、処理後に削除されます
- セッションデータはメモリ内に保存されるため、サーバー再起動時にリセットされます
