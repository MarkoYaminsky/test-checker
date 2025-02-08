from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "test-checker",
    broker=settings.celery_broker_url,
    backend=settings.celery_broker_url,
)

celery_app.conf.update(
    result_expires=3600,
    task_serializer="json",
)

celery_app.autodiscover_tasks(["app.student_tests.tasks"])
