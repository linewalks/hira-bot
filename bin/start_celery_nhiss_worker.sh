celery -A background.nhiss.celery worker -c 10 -Q nhiss_queue --pidfile="./nhiss.pid" --logfile="files/log/nhiss.log"
