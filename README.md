# TODO List
This is a simple application that allows you to manage your todo list (task manager)
## Main features
* Login/Registration/Authentication via VK social network.
* Creating goals:
    * You can choose the time interval of your goal and see the number of days until the end of your goal.
    * You can choose category of goal (personal, business, growth, sport, etc.)
    * You can choose priority of your goal (minor, major, critical)
    * You can manage the status of your goal(in progress, done, overdue, archived)
* Changing goals:
    * You can change the description of your goal.
    * You can change the status of your goal.
    * You are able to change priority and category of your goal.
* Remove goals:
    * When you delete your goal, the status changes to 'archived'.
* Search goal by title
* Filtering by the status, category, priority, year.
* Uploading goals to CSV/JSON format.
* Adding notes to your goal.
* Full work in the mobile app.
* Get all your goal by telegram bot.
* Create new goal by telegram bot.
## Technology stack   
Python v.3.11   
Poetry v.1.4.1   
Django v.4.1.7   
PostgreSQL   
Django REST Framework v.3.14.0  
django-pytest v.0.2.0   
pytest-factoryboy v.2.5.1   
VK OAuth2.0   
Gunicorn v.20.10.0   
Nginx   
Docker  
Docker-compose   
CI/CD pipeline by GitHub Actions
## Local start  
Create local .env file with the next data:  
``` python
SECRET_KEY='your django key'
DATABASE_URL=postgres://postgres:postgres@db/todo_list
DEBUG=True
VK_ID='your vk id'
VK_KEY='your vk secure key'
BOT_TOKEN='your bot token'
```
Run API, DB, Frontend and Migrations containers by:
``` python
docker-compose up --build
```
An application will run at http://localhost:80   
All features of telegram bot will be available with local start
## Server start 
Clone repository
``` python
git clone https://github.com/MichaelRodionov/TODOList.git
```
Create your own repository

Create GitHub Secrets in your repository with parameters:
``` python
# Django
SECRET_KEY  # django application secret key
# PostgreSQL
POSTGRES_USER  # your postgres username
POSTGRES_PASSWORD # your postgres password
POSTGRES_DB  # your postgres database name
# HOST
HOST  # your hostname (domain or IP address)
USER  # your host username
PASSWORD # your host password
# Docker
DOCKERHUB_TOKEN  # your dockerhub token
DOCKERHUB_USERNAME  # your dockerhub username
# VK OAuth2.0
VK_ID  # your VK application ID
VK_KEY  # your VK application secure key
# Telegram bot
BOT_TOKEN # your telegram bot token given by BotFather
```
Add remote to your GitHub repository by repository URL   
Push code to your repository
``` python
git add .  # add all files to Git
git commit -m 'add project'  # initial commit
git push  # push to repository
```
---
Deployment will be done automatically due to configured CI/CD process (GitHub Action pipeline) with the help of workflow todolist.yaml   
An application will run on your hostname   
All features of telegram bot will be available with server start
## Pytest
Core and Goal features are covered by 96% tests
## Database management   
A special postgres_adminer container has been launched for convenient database management and monitoring.  
By going to hostname:8080 you can send SQL queries, view tables, etc.
## OpenAPI documentation
You can open API documentation by hostname:8000/schema/redoc/
