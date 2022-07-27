# hw05_final

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)

## Социальная сель на Django.

## Установка 
1. Navigate to your projects directory.
2. Clone the repo from github and CD into project.
```shell
https://github.com/LittlePemp/hw05_final
```
3. Install PipEnv, if not already installed:
```shell
pip install -U pipenv
```
4. Create virtual environment.
```shell
pipenv install
```
If using a specific version of Python you may specify the path.
```shell
pipenv install --python PATH_TO_INTERPRETER
```
5. Activate environment.
```shell
pipenv shell
```
6. Apply migrations.
```shell
python manage.py migrate
```
7. Create a Development Django user.
```shell
python manage.py createsuperuser
```
8. Run development server.
```shell
python manage.py runserver
```
