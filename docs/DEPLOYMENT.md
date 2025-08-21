# Руководство по деплою Smart Cardiologist

## 🚀 Быстрый деплой

### 1. Подготовка к деплою

```bash
# Проверка готовности системы
make deploy-prepare

# Или полная проверка
python scripts/deploy_setup.py
```

### 2. Автоматический деплой

```bash
# Полный деплой (рекомендуется)
make deploy-full

# Или через скрипт
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## 📋 Требования к серверу

### Минимальные требования
- **CPU**: 2 ядра
- **RAM**: 4 GB
- **Диск**: 20 GB
- **ОС**: Linux (Ubuntu 20.04+)

### Рекомендуемые требования
- **CPU**: 4 ядра
- **RAM**: 8 GB
- **Диск**: 50 GB SSD
- **ОС**: Ubuntu 22.04 LTS

### Программное обеспечение
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: для клонирования репозитория

## 🔧 Пошаговый деплой

### Шаг 1: Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
```

### Шаг 2: Клонирование проекта

```bash
# Клонирование репозитория
git clone <your-repo-url> smart-cardiologist
cd smart-cardiologist

# Переключение на нужную ветку
git checkout main
```

### Шаг 3: Настройка переменных окружения

```bash
# Создание файла .env
cp .env.example .env

# Редактирование .env файла
nano .env
```

**Обязательные переменные:**
```env
# База данных
DB_PASSWORD=your_secure_password

# Безопасность
SECRET_KEY=your_secret_key_here

# API ключи
GROQ_API_KEY=your_groq_api_key

# Email настройки
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_email_password
```

### Шаг 4: Проверка готовности

```bash
# Проверка всех компонентов
python scripts/deploy_setup.py
```

### Шаг 5: Деплой

```bash
# Автоматический деплой
./scripts/deploy.sh

# Или пошагово
make docker-build
make docker-run
```

## 🐳 Docker деплой

### Сборка образа

```bash
# Сборка образа
docker build -t smart-cardiologist .

# Проверка образа
docker images smart-cardiologist
```

### Запуск контейнеров

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

### Управление контейнерами

```bash
# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Обновление
docker-compose pull
docker-compose up -d
```

## 🌐 Настройка домена и SSL

### 1. Настройка Nginx

Отредактируйте `nginx.conf`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://app:8000;
        # ... остальные настройки
    }
}
```

### 2. SSL сертификат (Let's Encrypt)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d your-domain.com

# Автоматическое обновление
sudo crontab -e
# Добавить: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Мониторинг и логи

### Просмотр логов

```bash
# Логи приложения
docker-compose logs app

# Логи базы данных
docker-compose logs postgres

# Логи Nginx
docker-compose logs nginx

# Все логи
docker-compose logs -f
```

### Мониторинг ресурсов

```bash
# Использование ресурсов
docker stats

# Проверка здоровья
curl http://localhost:8000/health
```

### Резервное копирование

```bash
# Резервная копия базы данных
docker-compose exec postgres pg_dump -U cardiologist smart_cardiologist > backup.sql

# Восстановление
docker-compose exec -T postgres psql -U cardiologist smart_cardiologist < backup.sql
```

## 🔄 Обновление системы

### 1. Обновление кода

```bash
# Получение обновлений
git pull origin main

# Пересборка и перезапуск
make deploy-full
```

### 2. Обновление ML-модели

```bash
# Переобучение модели
make train-ml

# Перезапуск приложения
docker-compose restart app
```

### 3. Обновление зависимостей

```bash
# Обновление requirements.txt
# Пересборка образа
docker-compose build --no-cache
docker-compose up -d
```

## 🛠️ Устранение неполадок

### Частые проблемы

#### 1. Порт занят
```bash
# Проверка занятых портов
sudo netstat -tulpn | grep :8000

# Остановка конфликтующих сервисов
sudo systemctl stop apache2  # если нужно
```

#### 2. Недостаточно памяти
```bash
# Проверка памяти
free -h

# Очистка Docker
docker system prune -a
```

#### 3. Проблемы с базой данных
```bash
# Проверка подключения
docker-compose exec postgres psql -U cardiologist -d smart_cardiologist

# Сброс базы данных
docker-compose down -v
docker-compose up -d
```

#### 4. ML-модель не загружается
```bash
# Переобучение модели
make train-ml

# Проверка файла модели
ls -la data/processed/medical_classifier.pkl
```

### Логи ошибок

```bash
# Детальные логи
docker-compose logs app --tail=100

# Логи с временными метками
docker-compose logs -t app
```

## 🔒 Безопасность

### 1. Firewall

```bash
# Настройка UFW
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. Обновления

```bash
# Автоматические обновления безопасности
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 3. Мониторинг безопасности

```bash
# Проверка уязвимостей
docker scout cves smart-cardiologist

# Обновление базовых образов
docker-compose pull
```

## 📈 Масштабирование

### Горизонтальное масштабирование

```bash
# Увеличение количества экземпляров приложения
docker-compose up -d --scale app=3
```

### Вертикальное масштабирование

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

## 📞 Поддержка

### Полезные команды

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

### Контакты

- **Документация**: `docs/`
- **Логи**: `logs/`
- **Конфигурация**: `config/`

## 🎯 Чек-лист деплоя

- [ ] Сервер подготовлен (Docker, Docker Compose)
- [ ] Код склонирован и обновлен
- [ ] Файл `.env` настроен
- [ ] ML-модель обучена (`make train-ml`)
- [ ] Проверка готовности пройдена (`make deploy-prepare`)
- [ ] Docker образ собран
- [ ] Контейнеры запущены
- [ ] База данных инициализирована
- [ ] Приложение отвечает на health check
- [ ] Домен и SSL настроены (опционально)
- [ ] Мониторинг настроен
- [ ] Резервное копирование настроено

**🎉 Поздравляем! Система готова к работе!**
