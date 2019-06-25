from django.shortcuts import render
from django.http import HttpResponse
from .models import Notifications,Exams,Subject


from .utils import insert_record, id_generator

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
    print("nextsection")
    body = examobj.body

    print(body)
    return render(request, 'new/exam.html',{'body': body})


def add(request):
    subject = Subject.objects.all()
    new_subject=""  #to be added by view add_sub
    return render(request, 'new/add.html', {'subject': subject,'new_subject':new_subject})


def add_topic(request):
    subject_id = request.POST.get('subject_id')
    print("subid")
    print(subject_id)
    topic_name = request.POST.get("topic_name")

    subject = Subject.objects.get(**{"subject_id": subject_id})
    data = {
        "topic_id": id_generator(o="topic", prefix="TOPC"),
        "subject_id": subject,
        "topicname": topic_name,
    }
    c = insert_record(data, o="topic")
    return HttpResponse("fuck")


def add_ques(request):
    return HttpResponse("fuck")


def add_sub(request):
    subject=Subject.objects.all()
    print("check1")
    new_subject = request.POST.get("Subject")
    print(new_subject)
    data = {
        "subject_name": new_subject,
        "subject_id": id_generator(o="sub", prefix="SU")
    }
    print('jj')
    insert_record(data, o="sub")
    print('jj')
    return render(request, 'new/add.html', {'subject': subject, 'new_subject':new_subject})