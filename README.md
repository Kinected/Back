# Kinected/Back

# Django-ninja api & Websockets server

# Setup :
## Virtual environment 
#### Create
```bash
conda create -n backend python
```
#### Activate
```bash
conda activate backend
```
#### Go to src/ directory
```bash
cd src
```
#### install packages
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



