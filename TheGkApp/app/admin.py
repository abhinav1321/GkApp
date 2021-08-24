from django.contrib import admin
from .models import Notifications
from .models import Exams
from .models import Subject
from .models import Topic
from .models import Questions
from .models import ExtendedUser, TestRecord, TestQuestions, OtpRegistration

# Register your models here.

admin.site.register(Notifications)
admin.site.register(Exams)
admin.site.register(Subject)
admin.site.register(Topic)
admin.site.register(Questions)
admin.site.register(TestRecord)
admin.site.register(TestQuestions)
admin.site.register(OtpRegistration)
admin.site.register(ExtendedUser)
