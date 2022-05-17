from uuid import uuid4

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

from apps.helpers.models import CreatedModel


def directory_path(instance, filename):
    return f'news/{timezone.now().strftime("%Y/%m/%d")}/{uuid4()}{filename}'


class Tag(models.Model):
    portal_id = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return f'{self.portal_id}: {self.name}'


class Article(CreatedModel):
    entity = JSONField(null=True)
    portal_id = models.IntegerField(unique=True, db_index=True)
    publish_date = models.DateTimeField()
    is_main = models.BooleanField(default=False)
    published = models.BooleanField(blank=True, default=True)
    title = models.CharField(max_length=400)
    description = models.TextField()
    image = models.ImageField(null=True)
    image_icon = models.ImageField(null=True)

    class Meta:
        abstract = True


class PharmMarketArticle(Article):
    tags = models.ManyToManyField(Tag, verbose_name='news_tag', related_name='pharm_market_articles')

    def __str__(self):
        return self.title


class CompanyArticle(Article):
    tags = models.ManyToManyField(Tag, verbose_name='news_tag', related_name='company_articles')

    def __str__(self):
        return self.title


class Birthday(models.Model):
    date = models.DateField()
    image = models.ImageField(null=True, upload_to=directory_path)
    job_title = models.CharField(max_length=128)
    name = models.CharField(max_length=128)


class PersonnelChange(models.Model):
    announce = models.CharField(max_length=512)
    image = models.ImageField(null=True, upload_to=directory_path)
    image_prev = models.ImageField(null=True, upload_to=directory_path)
    is_top = models.BooleanField()
    publish_date = models.DateField(null=True)
    text = models.TextField()
    title = models.CharField(max_length=128)
