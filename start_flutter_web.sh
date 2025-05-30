#!/bin/bash

echo "🚀 Flutter Web アプリを起動しています..."
echo "📍 アプリURL: http://localhost:3000"
echo "⏹️  停止するには Ctrl+C を押してください"
echo "-" * 50

cd flutter_app
flutter run -d web-server --web-port 3000 --web-hostname 0.0.0.0
