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
## Technology stack   
Python v.3.11   
Poetry v.1.4.1   
Django v.4.1.7   
Django REST Framework v.3.14.0   
VK OAuth2.0   
Docker
## Local start  
Create local .env file with the next data:  
``` python
SECRET_KEY='your django key'
DATABASE_URL=postgres://postgres:postgres@db/todo_list
DEBUG=True
VK_ID='your vk id'
VK_KEY='your vk secure key'
```
Run API, DB, Frontend and Migrations containers by:
``` python
docker-compose up --build
```
An application will run at http://localhost:80
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