# Приложение "Умный дом"

## Запуск проекта

### Сборка образа
```bash
docker-compose up --build
```
### Чтобы остановить контейнер
```bash
docker-compose down
```

### Чтобы запустить в фоновом режиме
```bash
docker-compose down
```

### Для миграций (при изменении бд)
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

Для остановки логов: Ctrl + C (просто два раза вводим, может подлагивать)  
Файлы Dockerfile и docker-compose.yml настроила, просьба их не трогать :) 

### Главная страница доступна по адресу:  
```bash
http://localhost:8000/
```  
### Админка:  
```bash
http://localhost:8000/admin
```

Создано командой:
1. Алина Каматали
2. Нерсисян Артем
3. Сухов Артем
4. Тарасов Федор 
5. Романов Александр