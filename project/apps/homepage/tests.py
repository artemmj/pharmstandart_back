import json
import logging
import pytest
import requests

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

logger = logging.getLogger('django')


@pytest.mark.django_db
def test_get_documents(client):
    email = 'aamakarenko@pharmstd.ru'
    password = 'dS168xV1^^^'

    response = client.post(
        reverse('api_v1:api-root:user-login'),
        data={'email': email, 'password': password}
    )
    assert response.status_code == status.HTTP_200_OK


# class HomepageApisTests(APITestCase):
#     def setUp(self):
#         self.email = 'aamakarenko@pharmstd.ru'
#         self.password = 'dS168xV1^^^'

#         resp = self.client.post(
#             reverse('api_v1:api-root:user-login'),
#             data={
#                 'email': self.email,
#                 'password': self.password,
#             }
#         )
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         self.token = json.loads(resp.content.decode('utf-8'))['token']

#     def test_get_counts(self):
#         """ Получить счетчики. """
#         resp = self.client.get(
#             reverse('api_v1:api-root:homepage-get-tasks-count'),
#             HTTP_AUTHORIZATION=f'JWT {self.token}',
#         )
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         jresp = json.loads(resp.content.decode('utf-8'))
#         if jresp['s_error']:
#             logger.info('Ошибка в получении счетчика задач.')
#         if jresp['Count'] < 0:
#             logger.info('Количество задач меньше нуля!')

#         resp = self.client.get(
#             reverse('api_v1:api-root:homepage-get-mails-count'),
#             HTTP_AUTHORIZATION=f'JWT {self.token}',
#         )
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         jresp = json.loads(resp.content.decode('utf-8'))
#         if jresp['s_error']:
#             logger.info('Ошибка в получении счетчика писем.')
#         if jresp['Count'] < 0:
#             logger.info('Количество писем меньше нуля!')

#     def test_get_documents(self):
#         resp = self.client.get(
#             reverse('api_v1:api-root:homepage-documents'),
#             HTTP_AUTHORIZATION=f'JWT {self.token}',
#         )
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         jresp = json.loads(resp.content.decode('utf-8'))
#         self.assertEqual(type(jresp), list)

#     def test_get_sliders(self):
#         resp = self.client.get(
#             reverse('api_v1:api-root:homepage-sliders'),
#             HTTP_AUTHORIZATION=f'JWT {self.token}',
#         )
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         jresp = json.loads(resp.content.decode('utf-8'))
#         self.assertEqual(type(jresp), list)

#     def test_get_tolls(self):
#         resp = self.client.get(
#             reverse('api_v1:api-root:homepage-tolls'),
#             HTTP_AUTHORIZATION=f'JWT {self.token}',
#         )
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         jresp = json.loads(resp.content.decode('utf-8'))
#         self.assertEqual(
#             list(jresp.keys()),
#             ['taxi', 'delivery_service', 'booking'],
#         )
