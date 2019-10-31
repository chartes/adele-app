# adele-app 
[![Build Status](https://travis-ci.org/chartes/adele-app.png?branch=dev)](https://travis-ci.org/chartes/adele-app?branch=dev)
[![Coverage Status](https://coveralls.io/repos/github/chartes/adele-app/badge.svg?branch=dev)](https://coveralls.io/github/chartes/adele-app?branch=dev)

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir db
```

The database must be fetched from https://github.com/chartes/adele and put in the db folder

Starting the server in debug mode:
```
gunicorn flask_app:flask_app -c gunicorn.conf.py
```


Building the front end:
```
cd app/client
npm install
npm run build
```
