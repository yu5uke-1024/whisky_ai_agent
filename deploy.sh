#!/bin/bash
# Cloud Build を実行してビルドとデプロイを行うスクリプト

# エラーが発生した場合はスクリプトを終了
set -e

echo "🚀 Cloud Build をトリガーして、ビルドとデプロイを開始します..."

# cloudbuild.yaml の設定を元に、現在のディレクトリをコンテキストとしてCloud Buildジョブをサブミット
gcloud builds submit --config cloudbuild_local.yaml .

echo "✅ Cloud Build ジョブが正常にサブミットされました。"
echo "進捗状況は Google Cloud Console の Cloud Build 履歴で確認してください。"
