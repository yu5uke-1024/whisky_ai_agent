# Whisky AI Agent - Flutter App & FastAPI Server

ウイスキーに関するAIエージェントのFlutterアプリとFastAPIサーバーです。

## 機能

### バックエンド（FastAPI）
- **POST /chat** - テキストと画像を受け取り、AIエージェントに問い合わせ
- **GET /health** - ヘルスチェック
- **GET /** - API情報
- multipart/form-data形式でのファイルアップロード対応
- 一時ファイル管理
- CORS対応（Flutter Webからのアクセス許可）

### フロントエンド（Flutter）
- テキスト入力とチャット機能
- 画像アップロード機能（file_picker使用）
- リアルタイムチャット履歴表示
- レスポンシブデザイン（Web・モバイル対応）
- エラーハンドリング
- ローディング状態表示

## セットアップ

### 1. Python依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. Flutter依存関係のインストール

```bash
cd flutter_app
flutter pub get
```

### 3. 環境変数の設定

`.env`ファイルを作成し、必要な環境変数を設定してください：

```env
# Google AI API Key
GOOGLE_API_KEY=your_api_key_here

# Firestore設定（必要に応じて）
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
```

## 起動方法

### 方法1: 個別起動

#### バックエンドサーバー起動
```bash
python start_server.py
```
または
```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

#### Flutter Webアプリ起動
```bash
./start_flutter_web.sh
```
または
```bash
cd flutter_app
flutter run -d web-server --web-port 3000
```

### 方法2: 同時起動（推奨）

2つのターミナルを開いて、それぞれで以下を実行：

**ターミナル1（バックエンド）:**
```bash
python start_server.py
```

**ターミナル2（フロントエンド）:**
```bash
./start_flutter_web.sh
```

## アクセス方法

- **Flutter Webアプリ**: http://localhost:3000
- **FastAPI サーバー**: http://localhost:8000
- **API ドキュメント**: http://localhost:8000/docs
- **ヘルスチェック**: http://localhost:8000/health

## 使用方法

1. Flutter Webアプリ（http://localhost:3000）にアクセス
2. テキスト入力欄にウイスキーに関する質問を入力
3. 必要に応じて画像ボタンからウイスキーの写真をアップロード
4. 送信ボタンを押してAIエージェントに問い合わせ
5. チャット履歴で過去のやり取りを確認

## API仕様

### POST /chat

**リクエスト形式**: multipart/form-data

**パラメータ**:
- `query` (string, required): ユーザーからのテキストクエリ
- `image` (file, optional): 画像ファイル（JPG、PNG、GIF、BMP）

**レスポンス**:
```json
{
  "response": "AIエージェントからの応答テキスト"
}
```

**エラーレスポンス**:
```json
{
  "detail": "エラーメッセージ"
}
```

## プロジェクト構造

```
whisky_ai_agent/
├── api_server.py              # FastAPIサーバー
├── start_server.py            # サーバー起動スクリプト
├── start_flutter_web.sh       # Flutter Web起動スクリプト
├── requirements.txt           # Python依存関係
├── flutter_app/               # Flutterアプリ
│   ├── lib/
│   │   └── main.dart         # メインアプリコード
│   ├── pubspec.yaml          # Flutter依存関係
│   └── ...
├── whisky_agent/             # AIエージェント
│   ├── agent.py
│   ├── sub_agents/
│   └── ...
└── utils.py                  # ユーティリティ関数
```

## 技術スタック

### バックエンド
- **FastAPI**: 高性能なPython Webフレームワーク
- **uvicorn**: ASGIサーバー
- **python-multipart**: multipart/form-data対応
- **google-adk**: Google AI Development Kit

### フロントエンド
- **Flutter**: クロスプラットフォームUIフレームワーク
- **http**: HTTP通信
- **file_picker**: ファイル選択
- **Material Design 3**: UIデザインシステム

## トラブルシューティング

### よくある問題

1. **CORS エラー**
   - FastAPIサーバーでCORS設定を確認
   - ブラウザの開発者ツールでネットワークエラーを確認

2. **画像アップロードエラー**
   - サポートされている画像形式（JPG、PNG、GIF、BMP）を使用
   - ファイルサイズが大きすぎないか確認

3. **API接続エラー**
   - バックエンドサーバーが起動しているか確認（http://localhost:8000/health）
   - ネットワーク設定を確認

4. **Flutter依存関係エラー**
   - `flutter clean && flutter pub get` を実行
   - Flutter SDKのバージョンを確認

### ログ確認

- **バックエンドログ**: サーバー起動時のターミナル出力
- **フロントエンドログ**: ブラウザの開発者ツール > Console

## 開発者向け情報

### カスタマイズ

- **APIエンドポイント変更**: `flutter_app/lib/main.dart`の`apiBaseUrl`を変更
- **UI カスタマイズ**: `flutter_app/lib/main.dart`のテーマ設定を変更
- **エージェント機能拡張**: `whisky_agent/`ディレクトリ内のファイルを編集

### デバッグモード

開発時は以下のコマンドでデバッグモードで起動：

```bash
# バックエンド（リロード有効）
uvicorn api_server:app --reload --log-level debug

# フロントエンド（ホットリロード有効）
cd flutter_app
flutter run -d web-server --web-port 3000
