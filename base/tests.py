from django.test import TestCase

from django.test import Client

class ViewTestCase(TestCase):
    def test_response_encoding(self):
        c = Client()
        response = c.get('127.0.0.1:8000/api/chats')
        content_type = response.get('Content-Type')
        print(content_type)
        self.assertIn('charset=utf-8', content_type)