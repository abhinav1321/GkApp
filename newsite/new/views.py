from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, JsonResponse
from .models import Notifications, Exams, Subject, Topic, Questions, ExtendedUser
import codecs
import csv
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import plotly.graph_objects as go
from django import forms
from .models import TestRecord
from django.views.generic.base import View

from .utils import insert_record, id_generator, set_maker,  set_maker_for_subject, analysis, otp_generator, otp_verifier
from .utils import calculator, test_record, record_questions_in_test_record, analysis1, overall_details, get_subject_list
from .utils import topics_user_analysis, subject_details, topic_details


# Create your views here.
def check_user_logged(request):
    """
    Checks if user is logged in
    :param request:
    :return: username if user logged in, else ''
    """
    username = ''
    if request.session.has_key('username'):
        username = request.session['username']
    return username


def index(request):
    """

    :param request:
    :return: an HTML render with username, notifications,
                                exams, subjects
    """
    username = ''
    session_variable = ''

    if request.method == 'POST':
        username = sign_in(request)[0]
        session_variable = sign_in(request)[1]
    if request.method == 'GET':
        sign_in(request)
    username = check_user_logged(request)

    notification = list(Notifications.objects.all())
    exam_list = list(Exams.objects.all())
    sub = list(Subject.objects.all())

    return render(request, 'new/index.html', {'notification': notification,
                                              'exam': exam_list,
                                              'subject': sub,
                                              'username': username,

                                              }
                  )


def exam(request):
    """
    Method : Post, retrieves data for requested exam object
    :param request:
    :return: HTML render of exam-body, notifications, session_variable, username
    """
    username = check_user_logged(request)

    notification = list(Notifications.objects.all())
    exam_name = request.POST.get('exam_name')
    session_variable = request.POST.get('session_variable')
    exam_obj = Exams.objects.get(**{"exam_name": exam_name})
    body = exam_obj.body

    return render(request, 'new/exam.html', {'body': body, 'notification': notification,
                                             'session_variable': session_variable,
                                             'username': username
                                             })


def get_topic(request):
    """
    gets topic details for a particular subject
    :param request:
    :return: HTML render with variables:- filtered topics, subject, username
    """

    username = check_user_logged(request)
    subject = request.POST.get('Subject_name')
    sub_obj = Subject.objects.all().filter(**{'subject_name': subject})

    for i in sub_obj:
        topic = Topic.objects.all().filter(**{'subject_id': i})

    return render(request, 'new/select_topic.html', {'topic': topic, 'Subject': subject, 'username': username})


def practice(request):
    """
    returns random questions for a Practice session

    :param request:
    :return: HTML render
    """
    username = check_user_logged(request)
    topic_name = request.POST.get('topicname')
    topic_object = Topic.objects.all().filter(**{'topicname': topic_name})
    questions = set_maker(topic_object[0].topic_id)
    subject = topic_object[0].subject_id
    q = []
    for ques in questions:
        i = 0
        q.append({"q_id": ques.q_id})
        i += 1

    test_obj = test_record(username, subject, topic=topic_object[0], test_type="S")
    print('taken test obj, semding forward', test_obj)
    record_questions_in_test_record(test_obj, question_list=q)

    return render(request, 'new/question_set.html', {
                                                        'questions': questions,
                                                        'q_id': q,
                                                        'len': len(q),
                                                        'topicname': topic_name,
                                                        'username': username,
                                                        'test_obj': test_obj.id
                                                    })


@login_required(login_url='login_view')
@staff_member_required
def add(request):
    """
    To Add new data directly, Admin only access
    :param request:
    :return: HTML render, subject_query, username
    """
    username = check_user_logged(request)
    subject = Subject.objects.all()
    new_subject = ""
    return render(request, 'new/add.html', {'subject': subject, 'new_subject': new_subject, 'username': username})


@login_required(login_url='login_view')
@staff_member_required
def add_topic(request):
    """
    Admin only, used to insert a new Topic
    :param request:
    :return: HttpResponse
    """
    username = check_user_logged(request)
    subject_id = request.POST.get('subject_id')
    topic_name = request.POST.get("topic_name")
    subject = Subject.objects.get(**{"subject_id": subject_id})
    data = {
        "topic_id": id_generator(o="topic", prefix="TOPC"),
        "subject_id": subject,
        "topicname": topic_name,
    }
    c = insert_record(data, o="topic")
    return HttpResponse("done")


@login_required(login_url='login_view')
@staff_member_required
def add_ques(request):
    """
    used to read the uploaded file for questions
    :param request:
    :return: HttpResponse done, if success
    """
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

            if insert_record(data=to_insert, o="question"):
                row_count = row_count + 1

        return HttpResponse("done")


@login_required(login_url='login_view')
@staff_member_required
def add_sub(request):
    """
    adding a new subject
    :param request:
    :return: HTML response, with subject and new_subject
    """
    subject = Subject.objects.all()
    new_subject = request.POST.get("Subject")
    data = {
        "subject_name": new_subject,
        "subject_id": id_generator(o="sub", prefix="SU")
    }
    insert_record(data, o="sub")
    return render(request, 'new/add.html', {'subject': subject, 'new_subject': new_subject})


def test_result(request):
    """
    This views does:
            1, calculate score with calculate function
            2.
    :param request:post request
    :return: Result
    """
    request_data = request.POST.copy()
    print(request_data)
    data = dict(request_data.items())
    del data['csrfmiddlewaretoken']
    questions = data.pop('question')
    test_obj = TestRecord.objects.get(pk=data.pop('test_obj'))
    print(test_obj, 'as test object post repsonse')
    d = dict(data)
    answer_list = []
    for k, v in d.items():
        answer_list.append((k, v))
    result = calculator(answer_list, test_obj)
    print(result)
    return render(request, 'new/test_result.html', {'result': result})


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
    data = request.GET.get('score')
    fig = go.Figure(go.Bar(
        x=[10, 6, int(data)],
        y=['giraffes', 'orangutans', 'monkeys'],
        orientation='h'))
    fig.write_image("records/fig1.png")
    return HttpResponse('ok')


class FormLogin(forms.Form):
    username = forms.CharField(label=("Username"), required=True)
    password = forms.CharField(label=("Password"), widget=forms.PasswordInput, required=True)


def login_view(request):
    return render(request, 'new/login_page.html')


def login_process(request):
    sign_in(request)
    return redirect('index')


def sign_in(request):
    username = None
    if request.method == 'GET':
        if 'action' in request.GET:
            if request.GET['action'] == 'logout':
                if request.session.has_key('username'):
                    request.session.flush()
                    logout(request)
                    return redirect('/')

    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        try:
            if user:
                ExtendedUser.objects.get(user=user)
                login(request, user)
                sess = request.session
                sess['username'] = username
                sess.set_expiry(900)

                # return username.upper(), sess
                return redirect('index')
            else:
                return redirect('incorrect_username_error')
        except Exception as e:
            print('Exception ', e)
            return redirect('internal_server_error')


def sign_up(request):

    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    try:
        s = User.objects.create_user(username, email, password)
        if s:
            ExtendedUser.objects.create(user=s)

        json_response = {'if_success': 1, 'comment': str(s)}
    except Exception as e:
        json_response = {'if_success': 0, 'comment': str(e)}
    return JsonResponse(json_response)


def jquery_step(request):
    return render(request, 'new/jquery.html')


def full_test(request):
    username = check_user_logged(request)
    subject_name = request.POST.get('Subject')
    sub_obj = Subject.objects.all().filter(**{'subject_name': subject_name})
    subject_id = sub_obj[0].subject_id
    q_id = []
    for s in sub_obj:
        set = set_maker_for_subject(s.subject_id)
        for s in set:
            q_id.append(s['q_id'])
    if set == 'questions less that 30':
        return HttpResponse('Could not create your test, Please go to home page')
    else:
        return render(request, 'new/test.html', {'username': username, 'set': set, 'q_id': q_id, 'subject': subject_name})


def full_test_result_calculator(request):
    username = check_user_logged(request)
    reply = request.POST.copy()
    reply_list = []
    for element in reply.items():
        reply_list.append(element)
    answered_list = reply_list[1:-2]
    asked_list = reply_list[-2][1][1:-1].split(',')
    subject_name = reply_list[-1][1]
    combined_list = []

    for n in asked_list:
        co = 0
        ans = ''

        for m in answered_list:
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
    # detail = analysis(user)
    detail = analysis1(user)
    print(detail)
    return render(request, 'new/user_analy.html', {
                                                    'username': user,
                                                    'detail': detail[0],
                                                    'sub_list': detail[1],
                                                    })


@login_required(login_url='login_view')
def user_analysis_new(request):
    user = check_user_logged(request)
    return render(request, 'new/user_analysis.html', {'username': user})


@login_required(login_url='login_view')
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


@login_required(login_url='login_view')
def verify(request):
    user = check_user_logged(request)
    verified = 'otp_failed'
    if request.method == 'POST':
        otp = request.POST.get('otp')
        otp_entry = request.POST.get('otp_entry')
        attempt = int(request.POST.get('attempt'))
        print(otp, otp_entry, attempt)

        if attempt < 3:
            verifier = otp_verifier(otp, otp_entry, user, verified)
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


def get_overall_details_for_user_analysis(request):
    username = request.POST.get('username')
    total_questions, attempted, correct, accuracy = overall_details(username)
    data = {
                'total_questions': str(total_questions),
                'attempted': str(attempted),
                'correct': str(correct),
                'accuracy': str(accuracy)
                }
    print(data)
    return JsonResponse(data)


def get_subjects_for_user_analysis(request):
    username = request.POST.get('username')
    print(username, 'subject_list_ua')

    print('username', username)
    subject_list = get_subject_list(username)
    return JsonResponse({'data': subject_list})


def get_subject_details_for_user_analysis(request):
    username = request.POST.get('username')
    subject_id = request.POST.get('subject')
    print(username, subject_id, 'subject_detail_ua')
    total_questions, attempted, correct, accuracy = subject_details(username, subject_id)
    data = {
        'total_questions': str(total_questions),
        'attempted': str(attempted),
        'correct': str(correct),
        'accuracy': str(accuracy)
    }
    print('retiurning data')
    return JsonResponse({subject_id: data})


def get_topics_for_user_analysis(request):
    username = request.POST.get('username')
    subject = request.POST.get('subject')
    topics = topics_user_analysis(username, subject)
    return JsonResponse({'data': topics})


def get_topics_details_for_user_analysis(request):
    username = request.POST.get('username')
    subject_id = request.POST.get('subject')
    topic = request.POST.get('topic')
    topic_data = topic_details(username, subject_id, topic)
    return JsonResponse({'data': topic_data})


class ErrorView(View):
    """
    Generic View for Errors,
        To customize, Go to urls.py , create new url with variable "error_name" inside
        e.g. => path('your_error_url', views.ErrorView.as_view(error_name="error 402"), name='your_error_url'),
    """
    error_name = "Oops! some error"

    def get(self, request, *args, **kwargs):
        return render(request, 'new/error_page.html', {'error': self.error_name})


def error_404(request, exception):
    return render(request, 'new/error_page.html', {'error': "Error 404"})


def error_500(request):
    return render(request, 'new/error_page.html', {'error': "Error 500"})
