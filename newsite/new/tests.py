from django.test import TestCase
from .models import Notifications, Subject, Exams, Questions
from datetime import datetime
from django.test.client import Client
from django.shortcuts import redirect


# Create your tests here.
class NotificationsTestCase(TestCase):
    def setUp(self):
        self.notification_id = Notifications.objects.create(notification='Test notification').id

    def test_pub_date(self):
        obj = Notifications.objects.get(id=self.notification_id)
        self.assertEquals(obj.pub_date.date(), datetime.now().date())


class IndexChecker(TestCase):
    def setup(self):
        self.client = Client()

    def test_index(self):
        response = self.client.get('http://localhost:8000/new/')
        self.assertTemplateUsed(response=response, template_name='new/index.html')

    def test_index_variables(self):
        response = self.client.get('http://localhost:8000/new/')

        subject = Subject.objects.all()
        sub = []
        for s in subject:
            sub.append(s.subject_name)

        self.assertEquals(response.context['subject'], sub)
        self.assertEquals(response.context['subject'], list(Notifications.objects.all()))
        self.assertEquals(response.context['subject'], sub)

