FROM python:3.11-slim

WORKDIR /app

# システムレベルの最適化
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 全依存関係をインストール（キャッシュ活用）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 必要なファイルのみコピー
COPY . .

EXPOSE 8080

# ADKマルチエージェントシステム用の起動設定（メモリとタイムアウト最適化）
CMD ["uvicorn", "line_bot_server:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1", "--timeout-keep-alive", "65", "--access-log"]