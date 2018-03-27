# adele-app


```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir db
```

The database will be fetched from https://github.com/chartes/adele each time the server is restarted.

Starting the server in debug mode:
```
python3 adele-app.py
```


Building the front end:
```
cd app/client
npm install
npm run build
```