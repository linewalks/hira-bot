from celery import Celery
from main import read_config

app = read_config()

celery = Celery(
    "nhiss",
    broker=app.config["NHISS_BROKER_URL"],
    backend=app.config["NOISS_RESULT_BACKEND"]
)

celery.conf.task_routes = {
    "nhiss.tasks.reservation_mode.*": {"queue": "nhiss_queue"}
}


def stop_celery_task(task_id):
  celery.control.revoke(task_id, terminate=True, signal="SIGKILL")


from nhiss.tasks.reservation_mode import run_until_success
