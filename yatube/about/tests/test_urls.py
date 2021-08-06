from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.static_pages_url_names = {
            'tech.html': reverse('about:tech'),
            'author.html': reverse('about:author')
        }

    def test_about_url_exists_at_desired_location(self):
        for template, adress in self.static_pages_url_names.items():
            response = self.guest_client.get(adress)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        for template, adress in self.static_pages_url_names.items():
            response = self.guest_client.get(adress)
            self.assertTemplateUsed(response, template)
