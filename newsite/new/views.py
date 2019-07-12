from django.shortcuts import render
from django.http import HttpResponse
from .models import Notifications,Exams,Subject,Topic, Questions
import codecs
import csv
import json


from .utils import insert_record, id_generator,set_maker

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
    notification = Notifications.objects.all()
    new_list = []
    for i in notification:
        new_list.append(i.notification)
    exam=request.POST.get('exam_name')

    examobj = Exams.objects.get(**{"exam_name": exam})
    print("nextsection")
    body = examobj.body

    print(body)
    return render(request, 'new/exam.html',{'body': body,'notification':new_list})


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
    file = request.FILES['fileup']
    rows = []
    if file.name.endswith(".csv"):
        data = csv.reader(codecs.iterdecode(file, 'utf-8'))
        row_count = -1
        for row in data:
            if row_count == -1:
                row_count = 0
                continue
            subject_id = Subject.objects.get(**{"subject_id": row[8]})
            topic_id = Topic.objects.get(**{"topic_id": row[9]})
            to_insert = {
                "q_id": row[0],
                "q_text": row[1],
                "a": row[2],
                "b": row[3],
                "c": row[4],
                "d": row[5],
                "e": row[6],
                "answer": row[7],
                "subject_id": subject_id,
                "topic_id": topic_id
            }

            print(to_insert)

            if insert_record(data=to_insert, o="question"):
                row_count = row_count + 1

        #        if rows[0] == ['q_id', 'q_text', 'a', 'b', 'c', 'd', 'answer']:
        #            print('yes')

        return HttpResponse("done")


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


def one_view(request):

    question= set_maker()
    return render (request, 'new/one_view.html' , {'question':question})

def calculator(answer_list=None):
    count =  0

    for question in answer_list:
        print(type(question))
        obj = Questions.objects.filter(**{"q_id": question[0]})
        print(question[0])
        print(obj[0].q_id)
        print(obj[0].answer)
        print(obj)
        if question[1] == obj[0].answer:
            count += 1

    return count

def count(request):
    reply = request.POST.copy()
    print(reply)
    x=reply.items()
    li =[]
    for element in x:
       li.append(element)

    result = calculator(answer_list=li[1:])

    if result <=5:
        review = "Improvement required"
    elif (result <=7):
        review = "GOOD Keep Going!"
    else:
        review = "WAaH bde log!"

    return render (request, 'new/result.html', {'review':review,'result':result})
