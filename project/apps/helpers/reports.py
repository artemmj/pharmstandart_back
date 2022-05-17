import os

from openpyxl import Workbook

from django.conf import settings
from django.utils import timezone


class Report:
    headers = []
    name = None

    def __init__(self):
        self.args = None
        self.kwargs = None

    def _filename(self):
        return f'{self.name if self.name else ""}{timezone.now().strftime("%d.%m_%H%M")}.xlsx'

    def _path(self):
        return f'reports/{timezone.now().strftime("%d%m")}'

    def _absolute_path(self):
        path = os.path.join(settings.MEDIA_ROOT, self._path())
        os.makedirs(path, exist_ok=True)
        return path

    def make_report(self, host, **kwargs):
        self.kwargs = kwargs

        wb = Workbook(write_only=True)
        ws = wb.create_sheet()

        if self.headers:
            ws.append(self.headers)

        for row in self.rows():
            ws.append(row)

        filename = self._filename()
        path = self._absolute_path()

        wb.save(os.path.join(path, filename))

        return host + os.path.join(self._path(), filename)

    def rows(self):
        # должен возвращать строки отчета, лучше делать генератором
        raise NotImplementedError()
