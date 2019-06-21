from django.shortcuts import render
from django.http import HttpResponse
from .models import Notifications,Exams,Subject


# Create your views here.
def index(request):
    notification = Notifications.objects.all()
    new_list=[]
    for i in notification:
        new_list.append(i.notification)
    check=[]
    exam=Exams.objects.all()
    body=[]
    for e in exam:
        body.append(e.exam_name)
    subject=Subject.objects.all()
    sub=[]
    for s in subject:
        sub.append(s.subject_name)
    print(sub)
    return render(request, 'new/index.html',{'notification': new_list,'exam':body,'subject':sub})


def exam(request):
    exam=request.POST.get('exam_name')
    print(exam)
    print("this one")
    examobj = Exams.objects.get(**{"exam_name": exam})
    body = examobj.body
    return render(request, 'new/exam.html',{'body': body},)
