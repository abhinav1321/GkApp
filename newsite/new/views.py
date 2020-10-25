from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, JsonResponse
from .models import Notifications, Exams, Subject, Topic, Questions
import codecs
import csv
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

import plotly.graph_objects as go
from django import forms
from formtools.wizard.views import SessionWizardView
import random
import datetime
from .mail import send_otp_mail


from .utils import insert_record, id_generator, \
                    set_maker, set_maker1, set_maker_for_subject, \
                    analysis, otp_generator, otp_verifier, analyse


# Create your views here.

def check_user_logged(request):
    username = ''

    if request.session.has_key('username'):
        username = request.session['username']

    return username


def index(request):

    username = ''
    session_variable = ''

    if request.method == 'POST':
        username = sign_in(request)[0]
        session_variable = sign_in(request)[1]
    if request.method == 'GET':
        print('here get')
        sign_in(request)

    username = check_user_logged(request)

    notification = Notifications.objects.all()
    new_list = []
    for i in notification:
        new_list.append(i.notification)
    new_list = new_list[::-1]
    exam = Exams.objects.all()
    body = []
    for e in exam:
        body.append(e.exam_name)
    subject = Subject.objects.all()
    sub = []
    for s in subject:
        sub.append(s.subject_name)
    print(sub)
    return render(request, 'new/index.html', {'notification': new_list,
                                              'exam': body,
                                              'subject': sub,
                                              'username': username,

                                              }
                  )


def exam(request):
    username = check_user_logged(request)

    notification = Notifications.objects.all()
    new_list = []
    for i in notification:
        new_list.append(i.notification)
    exam_name = request.POST.get('exam_name')
    session_variable = request.POST.get('session_variable')
    print(type(session_variable))

    exam_obj = Exams.objects.get(**{"exam_name": exam_name})
    body = exam_obj.body

    return render(request, 'new/exam.html', {'body': body, 'notification': new_list,
                                             'session_variable': session_variable,
                                             'username': username
                                             })


def get_topic(request):
    username = check_user_logged(request)
    subject = request.POST.get('Subject_name')
    sub_obj = Subject.objects.all().filter(**{'subject_name': subject})

    subject_id = sub_obj[0].subject_id
    for i in sub_obj:
        topic = Topic.objects.all().filter(**{'subject_id': i})

    return render(request, 'new/select_topic.html', {'topic': topic, 'Subject': subject, 'username': username})


def practice(request):
    username = check_user_logged(request)
    topic_name = request.POST.get('topicname')
    topic_object = Topic.objects.all().filter(**{'topicname': topic_name})
    # print(topic_object[0].topic_id)
    questions = set_maker1(topic_object[0].topic_id)
    q=[]
    for ques in questions:
        i = 0

        q.append({
            "q_id": ques.q_id,
        }
        )

        i = i + 1
    number_of_questions = len(q)

    return render(request, 'new/question_set.html', {'questions': questions,
                                                    'q_id': q,
                                                    'len': number_of_questions,
                                                    'topicname': topic_name,
                                                    'username': username
                                                    })


def add(request):
    username = check_user_logged(request)
    subject = Subject.objects.all()
    # 'new_subject'- Do not change variable, sent to template for adding subject
    new_subject = ""

    if username == '' or not User.objects.all().filter(**{'username': username})[0].is_superuser:

        return render(request, 'new/add.html', {'username': username, 'subject': subject, 'new_subject': new_subject, 'super_user': 'No'})

    return render(request, 'new/add.html', {'username': username, 'subject': subject, 'new_subject': new_subject, 'super_user': 'Yes'})


def add_topic(request):
    username = check_user_logged(request)

    subject_id = request.POST.get('subject_id')
    # print(subject_id)
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

            # print(to_insert)

            if insert_record(data=to_insert, o="question"):
                row_count = row_count + 1

        #        if rows[0] == ['q_id', 'q_text', 'a', 'b', 'c', 'd', 'answer']:
        #            print('yes')

        return HttpResponse("done")


def add_sub(request):
    username = check_user_logged(request)
    subject = Subject.objects.all()
    new_subject = request.POST.get("Subject")
    data = {
        "subject_name": new_subject,
        "subject_id": id_generator(o="sub", prefix="SU")
    }
    insert_record(data, o="sub")
    return render(request, 'new/add.html', {'subject': subject, 'new_subject' : new_subject})


def one_view(request):

    question = set_maker()
    q = []
    for ques in question:
        i = 0

        q.append({
            "q_id": ques.q_id,
        }
        )

        i = i+1

    return render(request, 'new/one_view.html', {'question': question, 'q_id': q})


def calculator(answer_list=None):
    count = 0
    for question in answer_list:
        obj = Questions.objects.filter(**{"q_id": question[0]})

        if question[1].lower() == obj[0].answer.lower():
            count += 1
            print(question[1], obj[0].answer, count)

    return count


def count(request):
    reply = request.POST.copy()
    x = reply.items()

    li = []
    for element in x:
       li.append(element)

    result = calculator(answer_list=li[1:-1])
    ques_asked = li[-1]

    question_list = []
    for q in ques_asked[1].replace("[", "").replace("]", "").split(", "):
        question_list.append(eval(q))

    y = []
    for a in question_list:
        y.append(a["q_id"])

    if result <= 5:
        review = "Improvement required"
    elif result <= 7:
        review = "GOOD Keep Going!"
    else:
        review = "WAaH bde log!"

    return render(request, 'new/result.html', {'review': review, 'result': result, 'id': y})


def export_csv(request):
    id = request.POST.get('id')
    li = list(id.replace("[", "").replace("]", "").split(", "))
    question = []
    for i in li:
        q = Questions.objects.all().filter(**{'q_id': i})
        question.append(q[0])

    response = HttpResponse(content_type='text/csv')
    response['Content_Disposition'] = 'attachment; filename="answer.csv"'
    writer = csv.writer(response)
    writer.writerow(["q_id", "q_text", "a", "b", "c", "d", "answer"])

    for item in question:
        writer.writerow([item.q_id, item.q_text, item.a, item.b, item.c, item.d, item.answer])

    return response


def plot(request):
    fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
    fig.write_html('first_figure.html')
    return render(request, 'new/first_figure.html')


class FormLogin(forms.Form):
    username = forms.CharField(label=("Username"), required=True)
    password = forms.CharField(label=("Password"), widget=forms.PasswordInput, required=True)


def session_demo(request):
    time = None
    username = None  # default value
    form_login = FormLogin()
    #print("check1")
    if request.method == 'GET':

        if 'action' in request.GET:
            action = request.GET.get('action')
            if action == 'logout':

                if request.session.has_key('username'):
                    request.session.flush()
                return redirect('sessions')

        if 'username' in request.session:
            username = request.session['username']
            
            print(
                request.session.get_expiry_date())
            # datetime.datetime object which represents the moment in time
            # at which the session will expire

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
                time = None

    return render(request, 'new/sessions.html', {
        'demo_title': 'Sessions in Django',
        'form': form_login,
        'username': username,
        'time': time
    })


def sign_in(request):
    time = None
    username = None
    if request.method == 'GET':
        print('check 1')
        if 'action' in request.GET:

            if request.GET['action'] == 'logout':
                print('here reached')
                if request.session.has_key('username'):
                    request.session.flush()
                    # request.session.set_expiry(0)
                    return redirect('/')

    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        # a = User.objects.all().filter(**())
        a=User.objects.all()
        for i in a:
            print(i)
        if user:
            sess = request.session
            sess['username'] = username
            sess.set_expiry(900)

            # request.session.set_expiry(900)
            # request.session['username']=username
            print('sess is ', sess)
            return username.upper(), sess
        else:
            return 'guest', ''


def sign_up(request):
    if request.is_ajax():
        print('yes ajax')
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    print(request.POST.copy())
    print(email)
    try:
        s = User.objects.create_user(username, email, password)
        print('here', str(s))
        json_response = {'if_success': 1, 'comment': str(s)}
    except Exception as e:
        print(e)
        json_response = {'if_success': 0, 'comment': str(e)}
    return JsonResponse(json_response)


# not yet complete
class FormWizardView(SessionWizardView):

    template_name = 'new/wizard.html'

    def done(self, form_list, **kwargs):
        form_data = process_form_data(form_list)
        return render_to_response('new/done.html', {'form_data': form_data})


def process_form_data(form_list):
    form_data = [form.cleaned_data for form in form_list]
    return form_data


def jquery_step(request):
    return render(request, 'new/jquery.html')


def new_ques_set(request):
    questions = set_maker()
    q = []
    for ques in questions:
        i = 0

        q.append({
            "q_id": ques.q_id,
        }
        )

        i = i + 1
    return render(request, 'new/question_set.html', {'questions': questions, 'q_id': q})


def full_test(request):
    username = check_user_logged(request)
    subject_name = request.POST.get('Subject')
    print(len(subject_name))
    sub_obj = Subject.objects.all().filter(**{'subject_name': subject_name})
    subject_id = sub_obj[0].subject_id
    q_id = []
    for s in sub_obj:
        set = set_maker_for_subject(s.subject_id)
        for s in set:
            q_id.append(s['q_id'])
    if set == 'questions less that 30':
        print('yes')

        return HttpResponse('Some error came, Please go to home page')
    else:
        return render(request, 'new/test.html', {'username': username,'set': set, 'q_id': q_id, 'subject': subject_name})


def test_record(username, subject, topic_wise):
    with open('records/test_record.csv', 'a') as file:
        writer = csv.writer(file)
        print('test entrtieioifhdoi')
        print('dskufh')
        test_id = str(username) + str(random.randint(10000, 99999))
        print(test_id, 'test id')
        data_time = datetime.datetime.now()
        print(test_id, data_time, 'as test id time')
        print(topic_wise)
        for k, v in topic_wise.items():
            topic = k
            ques_correct = v[1]
            ques_incorrect = v[2]
            ques_unattempted = v[3]
            ques_attempted = ques_correct + ques_incorrect
            ques_asked = ques_attempted + ques_unattempted
            score_in_the_topic = v[0]
            writer.writerow((test_id, data_time, username, subject,
                             topic,
                             ques_asked,
                             ques_attempted,
                             ques_correct,
                             ques_incorrect,
                             ques_unattempted,
                             score_in_the_topic))
        file.close()
    with open('records/test_record.csv', 'r+') as file2:
        reader = csv.reader(file2)
        for r in reader:
            print(r)
        file2.close()

def full_test_result_calculator(request):
    username = check_user_logged(request)
    reply = request.POST.copy()
    print(reply)
    reply_list = []
    for element in reply.items():
        reply_list.append(element)
    answered_list = reply_list[1:-2]
    asked_list = reply_list[-2][1][1:-1].split(',')
    subject_name = reply_list[-1][1]
    print(subject_name)
    print(answered_list)
    combined_list = []

    for n in asked_list:
        # print('check for ',n)
        co = 0
        ans = ''

        for m in answered_list:
            # print(m[0])
            if int(m[0]) == int(n):
                co = 1
                ans = m[1]
            else:
                pass
        if co == 1:
            combined_list.append((n, ans , 1))
        else:
            combined_list.append((n, '', 0))
    final_list = []
    for c in combined_list:
        marks = 0
        status = ''
        question_obj = Questions.objects.filter(q_id=c[0])
        for q in question_obj:
            topic = str(q.topic_id)
            actual_answer = q.answer
            if c[1] == actual_answer:
                marks = 1
                status = 'correct'
            elif c[1] == '':
                marks = 0
                status = 'unattempted'
            else:
                marks = (-1*(1/4))
                status = 'incorrect'
        ques_tuple = (c[0], status, marks, topic)
        final_list.append(ques_tuple)

    final_score = 0
    topic_wise = {}
    for item in final_list:
        final_score = float(final_score+float(item[2]))
    for item in final_list:
        correct, incorrect, unattempted = 0, 0, 0
        if item[1] == 'correct':
            correct = 1
        elif item[1] == 'incorrect':
            incorrect = 1
        elif item[1] == 'unattempted':
            unattempted = 1
        # list of score,correct,incorrect,unattempted
        if not str(item[3]) in topic_wise.keys():
            topic_wise[item[3]] = [float(item[2]), correct, incorrect, unattempted]

        else:
            topic_wise[item[3]][0] = topic_wise[item[3]][0] + float(item[2])
            topic_wise[item[3]][1] = topic_wise[item[3]][1] + correct
            topic_wise[item[3]][2] = topic_wise[item[3]][2] + incorrect
            topic_wise[item[3]][3] = topic_wise[item[3]][3] + unattempted

    for k, v in topic_wise.items():
        print(k, v)
    print(final_score)
    try:
        if not username == '':
            print('here to do the work')
            test_record(username, subject_name, topic_wise)
    except Exception as e:
        print(e)
    return render(request, 'new/score_result_full_test.html', {'topic_wise_details': topic_wise,
                                                               'score': final_score,
                                                               'username': username
                                                               })


def user_analysis(request):
    user = check_user_logged(request)

    detail = analysis(user)
    if detail == 'no data':
        return render(request, 'new/user_analy.html', {
            'username': user,
            'detail': detail[0],
            'sub_list': detail[1],
            'html_table': detail[2],
            'data': 'no'
        }
                      )

    return render(request, 'new/user_analy.html', {
                                                    'data': 'yes',
                                                    'username': user,
                                                    'detail': detail[0],
                                                    'sub_list': detail[1],
                                                    'html_table': detail[2],
                                                    }
                  )

    # detail = analyse(user)
    # return render(request, 'new/user_analysis.html', {'username': user, 'detail': detail})


def user_profile(request):
    user = check_user_logged(request)
    verified = 'not_verified'
    if not user == 'guest':

        with open('records/registered_user.csv', 'r') as file:
            reader = csv.reader(file)
            for r in reader:
                try:
                    if r[0] == user:
                        verified = 'verified'
                except Exception as e:
                    print(e)
            file.close()
    return render(request, 'new/profile.html', {'username': user,
                                                'verified': verified,
                                                })


def verify(request):
    user = check_user_logged(request)
    verified = 'otp_failed'
    if request.method == 'POST':
        otp = request.POST.get('otp')
        otp_entry = request.POST.get('otp_entry')
        # print(request.POST.get('attempt'))
        attempt = int(request.POST.get('attempt'))
        print(otp, otp_entry, attempt)

        if attempt < 3:
            verifier = otp_verifier(otp, otp_entry, user, verified)
            # print(verifier[1])
            verified = verifier[0]
            attempt = verifier[1]
            return render(request, 'new/profile.html', {'verified': verified,
                                                        'username': user,
                                                        'otp_entry': otp_entry,
                                                        'attempt': attempt
                                                        })
        else:
            return render(request, 'new/profile.html', {'verified': 'damage',
                                                        'username': user,
                                                        'otp_entry': 'not required'
                                                        })
    if request.method == 'GET':
        otp_entry = otp_generator(user)

        return render(request, 'new/profile.html', {'verified': 'otp_sent',
                                                    'username': user,
                                                    'otp_entry': otp_entry,
                                                    'attempt': 1
                                                    })
