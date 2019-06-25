from django.contrib import admin
from .models import Notifications
from .models import Exams
from .models import Subject
from .models import Topic
from .models import Questions

# Register your models here.

admin.site.register(Notifications)
admin.site.register(Exams)
admin.site.register(Subject)
admin.site.register(Topic)
admin.site.register(Questions)
