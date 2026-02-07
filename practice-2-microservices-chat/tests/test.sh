#!/bin/bash

echo "🧪 Тестирование микросервисного чата"
echo "=============================="

SOLUTION_DIR="../solution"
SCORE=0

# Тест 1: Проверка структуры
if [ -f "$SOLUTION_DIR/backend/Dockerfile" ]; then
    echo "✅ Dockerfile для backend найден"
    SCORE=$((SCORE + 10))
else
    echo "❌ Dockerfile для backend отсутствует"
fi

if [ -f "$SOLUTION_DIR/nginx/nginx.conf" ]; then
    echo "✅ Конфигурация nginx найдена"
    SCORE=$((SCORE + 10))
else
    echo "❌ Конфигурация nginx отсутствует"
fi

if [ -f "$SOLUTION_DIR/docker-compose.yml" ]; then
    echo "✅ docker-compose.yml найден"
    SCORE=$((SCORE + 10))
else
    echo "❌ docker-compose.yml отсутствует"
    exit 1
fi

# Тест 2: Копирование исходных файлов
cp -r ../starter-code/* "$SOLUTION_DIR/"

# Тест 3: Сборка и запуск
cd "$SOLUTION_DIR"
echo "🔨 Сборка контейнеров..."
docker compose build > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Сборка успешна"
    SCORE=$((SCORE + 20))
else
    echo "❌ Сборка не удалась"
    exit 1
fi

echo "🚀 Запуск сервисов..."
docker compose up -d > /dev/null 2>&1
sleep 10

# Тест 4: Проверка сервисов
if docker compose ps | grep -q "nginx.*Up"; then
    echo "✅ Nginx работает"
    SCORE=$((SCORE + 10))
fi

if docker compose ps | grep -q "backend.*Up"; then
    echo "✅ Backend работает"
    SCORE=$((SCORE + 10))
fi

if docker compose ps | grep -q "redis.*Up"; then
    echo "✅ Redis работает"
    SCORE=$((SCORE + 10))
fi

# Тест 5: Проверка API
API_RESPONSE=$(curl -s http://localhost/api/version)
if echo "$API_RESPONSE" | grep -q "version"; then
    echo "✅ API отвечает"
    SCORE=$((SCORE + 10))
    echo "   Версия: $(echo $API_RESPONSE | grep -o '"version":"[^"]*"')"
else
    echo "❌ API не отвечает"
fi

# Тест 6: Проверка frontend
if curl -s http://localhost | grep -q "Microservices Chat"; then
    echo "✅ Frontend доступен"
    SCORE=$((SCORE + 10))
else
    echo "❌ Frontend недоступен"
fi

# Очистка
docker compose down -v > /dev/null 2>&1

echo "=============================="
echo "📊 Итоговый балл: $SCORE/100"