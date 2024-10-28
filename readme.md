# Komaru Card Bot

## Запуск бота
1. Создайте и активируйте venv
```bash
python3 -m venv venv
 ```
2. Установите зависимости:
```bash
pip install -r requirements.txt
```
3. Подключите бд (например PostgreSQL) (сейчас это в loader.py, но в будущем это будет в config.yaml)
```python
from sqlalchemy import URL 

url = URL.create(
    drivername="postgresql+asyncpg",
    username="postgres",
    host="localhost",
    database="komaru_cards",
    password="postgres",
)
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
