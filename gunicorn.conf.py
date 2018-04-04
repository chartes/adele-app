import multiprocessing

bind = "localhost:5001"
workers = multiprocessing.cpu_count() * 2 + 1

reload=True
#accesslog='/var/log/flask/adele-app-access.log'
#errorlog='/var/log/flask/adele-app-error.log'

proc_name='adele'
