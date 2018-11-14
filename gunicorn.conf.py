import multiprocessing

bind = "localhost:5000"
workers = multiprocessing.cpu_count() * 2 + 1

reload=True
#accesslog='/var/log/flask/adele-app-access.log'
#errorlog='/var/log/flask/adele-app-error.log'
loglevel = 'debug'
proc_name='adele'

