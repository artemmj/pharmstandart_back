from django.db import models


class PharmSession(models.Model):
    id = models.UUIDField('ID сессии в апи фармы', primary_key=True)
    db_id = models.UUIDField('ID базы данных в апи фармы')

    def __str__(self):
        return str(self.id)
