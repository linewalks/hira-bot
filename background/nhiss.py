from celery import Celery

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
celery = Celery("nhiss", broker=BROKER_URL, backend=CELERY_RESULT_BACKEND)

celery.conf.task_routes = {
    "nhiss.tasks.reservation_mode.*": {"queue": "nhiss_queue"}
}


def stop_celery_task(task_id):
  celery.control.revoke(task_id, terminate=True, signal="SIGKILL")


from nhiss.tasks.reservation_mode import run_until_success
