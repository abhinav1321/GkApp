from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Notifications,Exams,Subject,Topic, Questions
import codecs
import csv
import json
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
import django.contrib.auth.models as mod
import plotly.graph_objects as go
from django import forms

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
    return HttpResponse("done")


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
    print("length")
    print(len(question))
    q=[]
    for ques in question:
        i=0

        q.append( {
            "q_id": ques.q_id,
        }
        )

        i=i+1

    return render (request, 'new/one_view.html' , {'question':question,'q_id':q})

def calculator(answer_list=None):
    count =  0

    for question in answer_list:
        obj = Questions.objects.filter(**{"q_id": question[0]})
        if question[1] == obj[0].answer:
            count += 1

    return count

def count(request):
    reply = request.POST.copy()

    x=reply.items()
    li =[]
    for element in x:
       li.append(element)

    result = calculator(answer_list=li[1:-1])
    ques_asked = li[-1]
    print(type(ques_asked))
    print(ques_asked)

    question_list = []
    for q in ques_asked[1].replace("[", "").replace("]", "").split(", "):
        question_list.append(eval(q))

    y = []
    for a in question_list:
        y.append(a["q_id"])
    print("y is")
    print(y)
    if result <=5:
        review = "Improvement required"
    elif (result <=7):
        review = "GOOD Keep Going!"
    else:
        review = "WAaH bde log!"

    return render (request, 'new/result.html', {'review':review,'result':result,'id':y})


def export_csv(request):

    id=request.POST.get('id')
    li = list(id.replace("[","").replace("]","").split(", "))
    question=[]
    for i in li:
        q = Questions.objects.all().filter(**{'q_id':i})
        question.append(q[0])

    response = HttpResponse(content_type='text/csv')
    response['Content_Disposition'] = 'attachment; filename="answer.csv"'
    writer = csv.writer(response)
    writer.writerow(["q_id", "q_text", "a", "b", "c", "d", "answer"])

    for item in question:
        writer.writerow([item.q_id,item.q_text,item.a,item.b,item.c,item.d,item.answer])


    return response


def plot(request):
    fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
    fig.write_html('first_figure.html')
    return render(request,'new/first_figure.html')



class FormLogin(forms.Form):
    username = forms.CharField(label=("Username"), required=True)
    password = forms.CharField(label=("Password"), widget=forms.PasswordInput, required=True)


def session_demo(request):
    time = None
    username = None  # default value
    form_login = FormLogin()
    print("check1")
    if request.method == 'GET':

        if 'action' in request.GET:
            action = request.GET.get('action')
            if action == 'logout':
                print('checkhere')
                if request.session.has_key('username'):
                    request.session.flush()
                return redirect('sessions')
        print('check2')
        if 'username' in request.session:
            username = request.session['username']
            print("time")
            print(request.session.get_expiry_age())  # session lifetime in seconds(from now)
            print(
                request.session.get_expiry_date())  # datetime.datetime object which represents the moment in time at which the session will expire
            print('check3')



    elif request.method == 'POST':
        form_login = FormLogin(request.POST)
        if form_login.is_valid():
            print('check4')
            username = form_login.cleaned_data['username']
            password = form_login.cleaned_data['password']
            if username.strip() == 'youtuber' and password.strip() == 'secret':
                request.session.set_expiry(300)
                request.session['username'] = username
                time = request.session.get_expiry_date()
            else:
                username = None
                time=None

    return render(request, 'new/sessions.html', {
        'demo_title': 'Sessions in Django',
        'form': form_login,
        'username': username,
        'time':time
    })

def signIn(request):
    time=None
    username=None
    if request.method== 'GET':
        if 'action' in request.GET:
            if 'action' == 'logout':
                if request.session.has_key['username']:
                    request.session.flush()
                    return redirect('')

    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            request.session.set_expiry(900)
            request.session['username']=username
            return render(request, 'new/base.html', {'username':username})

def hitview(request):
    username=request.POST.get('username')
    password=request.POST.get('email')
    email = request.POST.get('password')
    print(request.POST.copy())
    #User.objects.create_user(username,email,password)
    return HttpResponse("go and check admin")
