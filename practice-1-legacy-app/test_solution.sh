#!/bin/bash

echo "🧪 Тестирование решения..."

# Копируем решение
cp solution/* broken-weather-app/

cd broken-weather-app

# Запускаем
echo "🚀 Запускаем docker-compose..."
docker-compose up -d --build

# Ждем запуска
echo "⏳ Ожидаем запуска сервисов (30 сек)..."
sleep 30

# Проверяем health
echo "🏥 Проверяем health endpoint..."
curl -s http://localhost:5000/health | python -m json.tool

# Проверяем главную страницу
echo "🌐 Проверяем главную страницу..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000

# Проверяем API
echo "🌤️ Проверяем API погоды..."
curl -s http://localhost:5000/api/weather/Moscow | python -m json.tool

# Останавливаем
echo "🛑 Останавливаем контейнеры..."
docker-compose down -v

echo "✅ Тестирование завершено!"
