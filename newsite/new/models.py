from django.db import models
from django.utils import timezone
from datetime import datetime
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User


# Create your models here.
class ExtendedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)


class Notifications(models.Model):
    notification = models.TextField(max_length=300)
    pub_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.notification


class Exams(models.Model):
    exam_name= models.CharField(max_length=30)
    body = RichTextField(blank=True, null=True)

    def __str__(self):
        return self.exam_name


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
    e = models.CharField(max_length=300,null=True)
    q_rich = RichTextField(blank=True, null=True)
    answer = models.CharField(max_length=300)

    def __str__(self):
        return self.q_text

    class Meta:
        verbose_name_plural = "Question"


class TestRecord(models.Model):
    test_type = models.CharField(max_length=30, choices=(('S', "Short Test"), ('F', 'Full test')))
    subject = models.ForeignKey(Subject, null=True, on_delete=models.PROTECT)
    topic = models.ForeignKey(Topic, null=True, on_delete=models.PROTECT)
    user = models.ForeignKey(ExtendedUser, on_delete=models.PROTECT, null=True)
    date = models.DateTimeField(auto_now_add=True)


class TestQuestions(models.Model):
    test = models.ForeignKey(TestRecord, on_delete=models.CASCADE)
    question_id = models.ForeignKey(Questions, on_delete=models.CASCADE)
    attempted = models.BooleanField(default=False)
    correct_or_incorrect = models.BooleanField(default=False)


class OtpRegistration(models.Model):
    user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=10)
    date = models.DateTimeField(auto_now_add=True)
