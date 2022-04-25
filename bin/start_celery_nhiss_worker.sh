NUM_VCPUS=$(grep -c ^processor /proc/cpuinfo)
# celery -A background.nhiss.celery worker -c $((NUM_VCPUS / 2)) -Q nhiss_queue --pidfile="./nhiss.pid" --logfile="files/log/nhiss.log"
celery -A background.nhiss.celery worker -Q nhiss_queue --pidfile="./nhiss.pid" --logfile="files/log/nhiss.log"
