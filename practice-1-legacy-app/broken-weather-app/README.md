# Legacy Weather Application

## ⚠️ ВАЖНО: Это приложение требует сложной настройки окружения!

### Требования для запуска:

1. **Python 3.9.x** (Проверено только на этой версии, на других может не работать!)
2. **PostgreSQL 12** с созданной базой данных
3. **Redis 5.0+** для кэширования
4. **Системные пакеты** (Ubuntu/Debian):
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-dev python3-pip
   sudo apt-get install -y libpq-dev postgresql-client
   sudo apt-get install -y libxml2-dev libxslt1-dev
   sudo apt-get install -y libjpeg-dev zlib1g-dev
   sudo apt-get install -y gcc g++ make
   ```

### Инструкция по запуску:

1. Установите PostgreSQL и создайте базу:
   ```bash
   sudo -u postgres psql
   CREATE DATABASE weatherdb;
   CREATE USER weather WITH PASSWORD 'secret123';
   GRANT ALL PRIVILEGES ON DATABASE weatherdb TO weather;
   \q
   ```

2. Установите и запустите Redis:
   ```bash
   sudo apt-get install redis-server
   sudo service redis-server start
   ```

3. Создайте виртуальное окружение Python:
   ```bash
   python3.9 -m venv venv
   source venv/bin/activate
   ```

4. Установите зависимости Python:
   ```bash
   pip install --upgrade pip==22.0.4
   pip install setuptools==58.0.0
   pip install -r requirements.txt
   ```

5. Настройте переменные окружения:
   ```bash
   cp .env.example .env
   # Отредактируйте .env под ваши настройки
   source .env
   export DB_HOST DB_NAME DB_USER DB_PASS REDIS_HOST REDIS_PORT
   ```

6. Инициализируйте базу данных:
   ```bash
   python init_db.py
   ```

7. Запустите приложение:
   ```bash
   python app.py
   ```

8. Откройте http://localhost:5000

### Известные проблемы:
- Если видите ошибку с psycopg2, установите: `sudo apt-get install python3.9-dev`
- Если не работает Pillow, нужно: `sudo apt-get install libjpeg-dev`
- На Mac OS могут быть проблемы с версиями библиотек
- Приложение не запустится если хоть одна переменная окружения не настроена

### Что делает приложение:
- Показывает погоду для введенного города
- Кэширует результаты в Redis на 5 минут
- Сохраняет историю запросов в PostgreSQL
- Имеет health-check endpoint на /health