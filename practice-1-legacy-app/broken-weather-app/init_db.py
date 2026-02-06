#!/usr/bin/env python3
import psycopg2
import os

def init_database():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        database=os.getenv('DB_NAME', 'weatherdb'),
        user=os.getenv('DB_USER', 'weather'),
        password=os.getenv('DB_PASS', 'secret123')
    )
    
    cur = conn.cursor()
    
    # Создаем таблицу
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weather_logs (
            id SERIAL PRIMARY KEY,
            city VARCHAR(100) NOT NULL,
            temperature INTEGER,
            humidity INTEGER,
            description VARCHAR(200),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Создаем индекс
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_city_created 
        ON weather_logs(city, created_at DESC)
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()
