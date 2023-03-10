from django.test import Client, TestCase


class ViewTestClass(TestCase):
    def test_error_page(self):
        self.user_client = Client()
        response = self.client.get('/nonexist-page/')
        # Проверьте, что статус ответа сервера - 404
        # Проверьте, что используется шаблон core/404.html
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "core/404.html")
