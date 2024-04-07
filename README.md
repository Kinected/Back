# Kinected/Back

# Django-ninja api & Websockets server

# Setup :
## Virtual environment 
```bash
conda create -n backend python
```
```bash
conda activate backend
```
```bash
cd src
```
```bash
pip install -r requirements.txt
```
## Migrations
```bash
python manage.py makemigrations api
```
```bash
python manage.py migrate
```
## Launch Docker
```bash
docker run --rm -p 6379:6379 redis:7
```
## Launch App
```bash
python manage.py runserver
```

## Createsuperuser
```bash
python manage.py createsuperuser
```




