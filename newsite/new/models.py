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


class Topic(models.Model):
    topic_id = models.CharField(max_length=10)
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topicname = models.CharField(max_length=100)
    content = models.FileField(null=True)

    def __str__(self):
        return self.topicname

    class Meta:
        verbose_name_plural = "Topic"


class Questions(models.Model):
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic_id = models.ForeignKey(Topic, on_delete=models.CASCADE)

    q_id = models.IntegerField()
    q_text = models.CharField(max_length=300)
    a = models.CharField(max_length=300)
    b = models.CharField(max_length=300)
    c = models.CharField(max_length=300)
    d = models.CharField(max_length=300)
    answer = models.CharField(max_length=300)

    def __str__(self):
        return self.q_text

    class Meta:
        verbose_name_plural = "Question"

