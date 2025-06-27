#!/bin/bash
# ステージング環境用のCloud Build デプロイスクリプト

# エラーが発生した場合はスクリプトを終了
set -e

# カラー出力用の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 ステージング環境へのデプロイを開始します...${NC}"

# 現在のブランチ名を取得
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
COMMIT_SHA=$(git rev-parse --short HEAD)

echo -e "${YELLOW}📋 デプロイ情報:${NC}"
echo -e "  ブランチ: ${CURRENT_BRANCH}"
echo -e "  コミット: ${COMMIT_SHA}"
echo -e "  環境: ステージング"
echo -e "  サービス名: whisky-line-bot-staging"

# 確認プロンプト
read -p "$(echo -e ${YELLOW}この設定でデプロイを続行しますか？ [y/N]: ${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ デプロイをキャンセルしました。${NC}"
    exit 1
fi

echo -e "${BLUE}🔨 Cloud Build ジョブを開始しています...${NC}"

# cloudbuild_staging.yaml の設定を元に、現在のディレクトリをコンテキストとしてCloud Buildジョブをサブミット
gcloud builds submit \
    --config ./build/cloudbuild_staging.yaml \
    --substitutions SHORT_SHA=${COMMIT_SHA},BRANCH_NAME=${CURRENT_BRANCH} \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ ステージング環境へのデプロイが正常に完了しました！${NC}"
    echo -e "${BLUE}📊 デプロイ後の確認:${NC}"
    
    # サービスURLを取得
    SERVICE_URL=$(gcloud run services describe whisky-line-bot-staging --region=asia-northeast1 --format='value(status.url)')
    
    echo -e "  サービスURL: ${SERVICE_URL}"
    echo -e "  ヘルスチェック: ${SERVICE_URL}/health"
    echo -e "  Webhook URL: ${SERVICE_URL}/webhook"
    
    echo -e "${YELLOW}🔍 ログの確認:${NC}"
    echo -e "  gcloud logs tail --service=whisky-line-bot-staging"
    
    echo -e "${YELLOW}📈 モニタリング:${NC}"
    echo -e "  Google Cloud Console の Cloud Run セクションで詳細を確認してください。"
    
else
    echo -e "${RED}❌ デプロイに失敗しました。Cloud Build のログを確認してください。${NC}"
    exit 1
fi