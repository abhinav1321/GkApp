from django.db import models
from django.utils import timezone
from datetime import datetime
from ckeditor.fields import RichTextField


# Create your models here.
class Notifications(models.Model):
    notification = models.TextField(max_length=300)
    pub_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.notification


class Exams(models.Model):
    exam_name= models.CharField(max_length=30)
    body = RichTextField(blank=True, null=True)



class Subject(models.Model):

    subject_name = models.CharField(max_length=100)
    subject_id = models.CharField(max_length=10)

    def __str__(self):
        return self.subject_name

    class Meta:
        verbose_name_plural = "Subject"
