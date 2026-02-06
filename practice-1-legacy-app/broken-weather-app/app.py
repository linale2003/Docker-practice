import os
import sys
import psycopg2
import redis
import requests
from flask import Flask, render_template, jsonify
from flask_cors import CORS
import configparser
from datetime import datetime
import pytz
import numpy as np
from PIL import Image
import io

# Эта штука нужна для правильной работы с кириллицей
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

app = Flask(__name__)
CORS(app)

# Читаем конфиг
config = configparser.ConfigParser()
config.read('config.ini')

# Подключение к Redis
try:
    r = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        decode_responses=True
    )
except:
    print("WARNING: Redis не подключен, кэш работать не будет")
    r = None

# Подключение к PostgreSQL
def get_db():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        database=os.getenv('DB_NAME', 'weatherdb'),
        user=os.getenv('DB_USER', 'weather'),
        password=os.getenv('DB_PASS', 'secret123')
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/weather/<city>')
def get_weather(city):
    # Проверяем кэш
    if r:
        cached = r.get(f"weather:{city}")
        if cached:
            return jsonify({"city": city, "data": cached, "source": "cache"})
    
    # Получаем погоду от API
    api_key = os.getenv('WEATHER_API_KEY', 'demo_key_12345')
    
    # Симулируем вызов API погоды
    weather_data = {
        "temperature": np.random.randint(15, 30),
        "humidity": np.random.randint(40, 80),
        "description": np.random.choice(["Sunny", "Cloudy", "Rainy"]),
        "timestamp": datetime.now(pytz.timezone('Europe/Moscow')).isoformat()
    }
    
    # Сохраняем в БД
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO weather_logs (city, temperature, humidity, description, created_at) VALUES (%s, %s, %s, %s, %s)",
            (city, weather_data['temperature'], weather_data['humidity'], weather_data['description'], datetime.now())
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")
    
    # Кэшируем на 5 минут
    if r:
        r.setex(f"weather:{city}", 300, str(weather_data))
    
    return jsonify({"city": city, "data": weather_data, "source": "api"})

@app.route('/api/history/<city>')
def get_history(city):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT temperature, humidity, description, created_at FROM weather_logs WHERE city = %s ORDER BY created_at DESC LIMIT 10",
            (city,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        history = [
            {
                "temperature": row[0],
                "humidity": row[1],
                "description": row[2],
                "timestamp": row[3].isoformat()
            }
            for row in rows
        ]
        
        return jsonify({"city": city, "history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    checks = {
        "app": "ok",
        "redis": "ok" if r and r.ping() else "fail",
        "database": "ok"
    }
    
    try:
        conn = get_db()
        conn.close()
    except:
        checks["database"] = "fail"
    
    status = 200 if all(v == "ok" for v in checks.values()) else 503
    return jsonify(checks), status

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
