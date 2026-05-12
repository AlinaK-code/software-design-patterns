#!/bin/bash

# написала скрипт, чтобы при пересборки контейнеров каждый раз не создавать суперпользователя
# --noinput чтобы скрипт не зависал
python manage.py migrate --noinput

# для удобства пароли и логины админа указала явно (если забыли, см 11 строчку), надо будет - сделаю переменные окружения
python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'cookielover555')
    print("Superuser 'admin' created.")
else:
    print("Superuser 'admin' already exists.")
EOF

exec "$@"