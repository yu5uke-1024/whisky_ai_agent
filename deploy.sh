#!/bin/bash

# Cloud Run デプロイスクリプト
set -e

echo "🚀 Cloud Run デプロイを開始します..."

# プロジェクト設定
PROJECT_ID="whisky-ai-project"
REGION="asia-northeast1"
SERVICE_NAME="whisky-line-bot"
IMAGE_NAME="whisky-line-bot-multi-agent"
REPOSITORY="whisky-ai-repo"
IMAGE_TAG="v1.0"

IMAGE_URL="asia-northeast1-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "📦 Docker イメージをビルド・プッシュしています..."
gcloud builds submit --config cloudbuild.yaml

echo "🔄 Cloud Run サービスを更新しています..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_URL \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10

echo "✅ デプロイが完了しました!"
echo "🌐 サービスURL: https://whisky-line-bot-940978794346.asia-northeast1.run.app"
