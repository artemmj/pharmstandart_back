import os

from django.conf import settings

from apps import app
from api.v1.news.loaders.news import CompanyNewsLoader, PharmMarketNewsLoader
from api.v1.news.loaders.birthdays import BirthdaysLoader
from api.v1.news.loaders.personnel_changes import PersonnelChangesLoader


def check_news_dir():
    if not os.path.exists(settings.MEDIA_ROOT + '/news'):
        os.mkdir(settings.MEDIA_ROOT + '/news')


@app.task
def update_company_news():
    check_news_dir()
    CompanyNewsLoader().load()


@app.task
def update_pharm_news():
    check_news_dir()
    PharmMarketNewsLoader().load()


@app.task
def update_bithdays_news():
    check_news_dir()
    BirthdaysLoader().load()


@app.task
def update_personnel_changes_news():
    check_news_dir()
    PersonnelChangesLoader().load()
