# 🚀 Чек-лист деплоя Smart Cardiologist

## ✅ Подготовка к деплою

### 1. **Проверка системы**
```bash
# Проверка готовности
make deploy-prepare

# Или полная проверка
python scripts/deploy_setup.py
```

### 2. **Настройка переменных окружения**
Создайте файл `.env` на основе `.env.example`:

```env
# База данных
DATABASE_URL=postgresql://cardiologist:your_password@localhost:5432/smart_cardiologist
DB_PASSWORD=your_secure_password

# Безопасность
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API ключи
GROQ_API_KEY=your_groq_api_key_here

# Email настройки
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_email_password
EMAIL_FROM=your_email@gmail.com

# Redis
REDIS_URL=redis://localhost:6379

# Настройки приложения
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 3. **Обучение ML-модели**
```bash
# Обучение модели (если еще не обучена)
make train-ml
```

## 🐳 Docker деплой

### 1. **Сборка образа**
```bash
# Сборка Docker образа
make docker-build

# Или напрямую
docker build -t smart-cardiologist .
```

### 2. **Запуск контейнеров**
```bash
# Запуск всех сервисов
make docker-run

# Или напрямую
docker-compose up -d
```

### 3. **Проверка статуса**
```bash
# Статус контейнеров
docker-compose ps

# Логи приложения
docker-compose logs app

# Проверка здоровья
curl http://localhost:8000/health
```

## 🔧 Ручной деплой (без Docker)

### 1. **Подготовка сервера**
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и зависимостей
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx

# Установка зависимостей
pip install -r requirements.txt
```

### 2. **Настройка базы данных**
```bash
# Создание пользователя и базы данных
sudo -u postgres psql
CREATE USER cardiologist WITH PASSWORD 'your_password';
CREATE DATABASE smart_cardiologist OWNER cardiologist;
GRANT ALL PRIVILEGES ON DATABASE smart_cardiologist TO cardiologist;
\q

# Применение миграций
alembic upgrade head
```

### 3. **Запуск приложения**
```bash
# Запуск в продакшене
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# Или через systemd
sudo systemctl enable smart-cardiologist
sudo systemctl start smart-cardiologist
```

## 🌐 Настройка веб-сервера

### 1. **Nginx конфигурация**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. **SSL сертификат**
```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d your-domain.com
```

## 📊 Мониторинг и обслуживание

### 1. **Проверка логов**
```bash
# Логи приложения
tail -f logs/app.log

# Логи Nginx
sudo tail -f /var/log/nginx/access.log

# Логи базы данных
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### 2. **Резервное копирование**
```bash
# Резервная копия базы данных
pg_dump -U cardiologist smart_cardiologist > backup_$(date +%Y%m%d).sql

# Восстановление
psql -U cardiologist smart_cardiologist < backup_20240821.sql
```

### 3. **Обновление системы**
```bash
# Обновление кода
git pull origin main

# Пересборка и перезапуск
make deploy-full
```

## 🛠️ Устранение неполадок

### Частые проблемы:

#### 1. **Порт 8000 занят**
```bash
# Проверка
sudo netstat -tulpn | grep :8000

# Остановка конфликтующих сервисов
sudo systemctl stop apache2
```

#### 2. **ML-модель не загружается**
```bash
# Переобучение модели
make train-ml

# Проверка файла
ls -la data/processed/medical_classifier.pkl
```

#### 3. **База данных недоступна**
```bash
# Проверка статуса PostgreSQL
sudo systemctl status postgresql

# Перезапуск
sudo systemctl restart postgresql
```

#### 4. **Недостаточно памяти**
```bash
# Проверка памяти
free -h

# Очистка Docker (если используется)
docker system prune -a
```

## 🔒 Безопасность

### 1. **Firewall**
```bash
# Настройка UFW
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. **Обновления безопасности**
```bash
# Автоматические обновления
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 📈 Масштабирование

### 1. **Горизонтальное масштабирование**
```bash
# Увеличение количества воркеров
docker-compose up -d --scale app=3
```

### 2. **Вертикальное масштабирование**
Отредактируйте `docker-compose.yml`:
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
```

## 🎯 Финальная проверка

### После деплоя проверьте:

- [ ] Приложение отвечает на `http://localhost:8000/health`
- [ ] API документация доступна на `http://localhost:8000/docs`
- [ ] База данных подключена и работает
- [ ] ML-модель загружается корректно
- [ ] Трёхуровневая система фильтрации работает
- [ ] Логи не содержат критических ошибок
- [ ] SSL сертификат настроен (если используется домен)
- [ ] Резервное копирование настроено
- [ ] Мониторинг работает

## 📞 Поддержка

### Полезные команды:
```bash
# Статус системы
make health

# Проверка готовности
make deploy-check

# Очистка системы
make docker-clean

# Полная переустановка
make docker-clean && make deploy-full
```

### Контакты:
- **Документация**: `docs/`
- **Логи**: `logs/`
- **Конфигурация**: `config/`

---

## 🎉 Поздравляем!

Если все пункты чек-листа выполнены, ваша система Smart Cardiologist успешно развернута и готова к работе!

**Доступные URL:**
- 🌐 Приложение: `http://localhost:8000`
- 📚 API документация: `http://localhost:8000/docs`
- 🗄️ База данных: `localhost:5432`
- 🔄 Redis: `localhost:6379`
