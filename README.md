# adele-app 

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir db
```

The database must be fetched from https://github.com/chartes/adele and put in the db folder

Starting the server in debug mode:
```
python flask_app.py
```


Building the front end:
```
cd app/client
npm install
npm run build
```
