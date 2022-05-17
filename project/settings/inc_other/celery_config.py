import os

from celery.schedules import crontab

from ..common import env


BROKER_URL = os.environ.get('BROKER_URL', 'redis://redis/14')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis/15')
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = env('TIME_ZONE', str, 'Europe/Moscow')
CELERYBEAT_SCHEDULE = {
    "update_company_news_task": {
        "task": "apps.news.tasks.update_company_news",
        "schedule": crontab(hour=1, minute=0),
    },
    "update_pharm_news_task": {
        "task": "apps.news.tasks.update_pharm_news",
        "schedule": crontab(hour=1, minute=15),
    },
    "update_bithdays_news_task": {
        "task": "apps.news.tasks.update_bithdays_news",
        "schedule": crontab(hour=1, minute=30),
    },
    "update_personnel_changes_news_task": {
        "task": "apps.user.tasks.update_personnel_changes_news",
        "schedule": crontab(hour=2, minute=45),
    },
    "actualize_org_structure_task": {
        "task": "apps.data_center.tasks.actualize_org_structure",
        "schedule": crontab(hour=3, minute=0),
    },
}
