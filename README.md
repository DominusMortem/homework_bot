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
Django==2.2.16
pytest==6.2.4
pytest-pythonpath==0.7.3
pytest-django==4.4.0
djangorestframework==3.12.4
djangorestframework-simplejwt==4.7.2
Pillow==8.3.1
PyJWT==2.1.0
requests==2.26.0
```
