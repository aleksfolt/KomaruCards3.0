# DEPRECATED
- ACTUAL LINK: GITHUB.COM/FAUSTYU1/CARDSBOT

# [Komaru Cards Bot](https://github.com/aleksfolt/KomaruCards3.0)

# Оглавление
- [Запуск бота](#запуск-бота)
- [Актуализация статуса групп и пользователей](#актуализация-статуса-групп-и-пользователей)
- [Подготовка файлов к транспортировке в прод](#подготовка-файлов-к-транспортировке-в-прод)

## Запуск бота
![14.mp4](md/14.gif)
1. Создайте и активируйте venv
```bash
python3 -m venv venv
source venv/bin/activate
 ```
2. Установите зависимости:
```bash
pip install -r requirements.txt
```
3. Создайте и заполните файл config.yaml
```yaml
bot:
  telegram:
    token: "token"
  cryptoPay:
    token: "token"
  flyer:
    token: "token"
  admins: [77000]
database:
  driver: "postgresql+asyncpg"
  host: "localhost"
  port: 5432
  database: "komaru_cards"
  user: "postgres"
  password: "postgres"
```
4. Запустите бота
```bash
python3 main.py
```


## Актуализация статуса групп и пользователей
Для актуализации статуса используйте update_status.py, необходимо подключение к бд и боту
```bash
python3 update_status.py
```
Это очень медленный процесс, поэтому не советую часто запускать его

Планирую чуть позже реализовать отображение состояния скрипта, но пока есть только SQL скриптик

```postgresql
SELECT 'users' AS category,
       COUNT(id) AS total_count,
       COUNT(CASE WHEN in_pm = true THEN 1 END) AS can_connect
FROM users
UNION ALL
SELECT 'groups' AS category,
       COUNT(id) AS total_count,
       COUNT(CASE WHEN in_group = true THEN 1 END) AS in_group_count
FROM groups;


```

## Подготовка файлов к транспортировке в прод
Что бы не отправлять свой pycache на сервер, используйте это:
```bash
python -m scripts.delete_pycache 
```

## Дополнительные условия использования

Если вы хотите изменить или перераспространить код, вы должны:
1. Создать форк репозитория (fork).
2. Вносить изменения в ваш форк и ссылаться на оригинальный репозиторий.

Любые изменения в коде должны быть доступны через ваш публичный форк.
