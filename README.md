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
## Local start
Create and activate virtual environment
``` python
python3 -m venv venv
source /venv/bin/activate
```
Install and activate poetry
``` python
pip install poetry
poetry init
```
Install dependencies
``` python
poetry install
```
Create an `.env` file and fill it in according to the listed fields in the env_example.txt file in the project root folder.

Install PostgreSQL   
``` python
# install homebrew for MacOS
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

# install postgres
brew install postgresql@15
```
Create database   
``` python
CREATE DATABASE <database name>;

# enter database with current user
psql -U <username> -d <database name>

# create user with password
CREATE USER <username> WITH PASSWORD <password>;

# give priveleges to new user
GRANT ALL PRIVILEGES ON <database name> TO <username>;
```
Make and run migrations
``` python
./manage.py makemigrations
./manage.py migrate
```
Run local server
``` python
./manage.py runserver
```
Show tables
``` python
# enter database
export DATABASE_URL=postgres://<username>:<password>@localhost:5432/<database>
psql $DATABASE_URL
# show all tables
\dp
```