# adele-app 
[![Build Status](https://travis-ci.org/chartes/adele-app.png)](https://travis-ci.org/chartes/adele-app)
[![Coverage Status](https://coveralls.io/repos/github/chartes/adele-app/badge.svg?branch=master)](https://coveralls.io/github/chartes/adele-app?branch=master)

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir db
```

The database will be fetched from https://github.com/chartes/adele each time the server is restarted.

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
