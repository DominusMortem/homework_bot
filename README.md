# Ассистент бот

Обновляет информацию через API Яндекс.Практикум о текущем статусе сданной на проверку работы.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/DominusMortem/homework_bot
```

```
cd homework_bot
```
Cоздать и активировать виртуальное окружение:
```
python -m venv venv
```
```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
Внести необходимые данные окружения в .env

Запустить проект:

```
python homework.py
```

### Зависимости:

```
Python==3.7
flake8==3.9.2
flake8-docstrings==1.6.0
pytest==6.2.5
python-dotenv==0.19.0
python-telegram-bot==13.7
requests==2.26.0
```
