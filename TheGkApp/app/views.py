from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, JsonResponse
from .models import Notifications, Exams, Subject, Topic, Questions, ExtendedUser, TestQuestions
import codecs
import csv, json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import TestRecord
from django.views.generic.base import View

from .utils import insert_record, id_generator, set_maker,  set_maker_for_subject, analysis, write_test_to_pdf, test_details
from .utils import calculator, test_record, record_questions_in_test_record, overall_details, get_subject_list, check_result
from .utils import topics_user_analysis, subject_details, topic_details, otp_creation, otp_verification, create_test


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

    return render(request, 'app/index.html', {'notification': notification,
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

    return render(request, 'app/exam.html', {'body': body, 'notification': notification,
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

    return render(request, 'app/select_topic.html', {'topic': topic, 'Subject': subject, 'username': username})


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
        q.append({"q_id": ques.id})
        i += 1

    test_obj = test_record(username, subject, topic=topic_object[0], test_type="S")
    record_questions_in_test_record(test_obj, question_list=q)

    return render(request, 'app/question_set.html', {
                                                        'questions': questions,
                                                        # 'q_id': q,
                                                        # 'len': len(q),
                                                        'topicname': topic_name,
                                                        'username': username,
                                                        'test_obj': test_obj.id
                                                    })


@login_required(login_url='login_view')
@staff_member_required
def add(request):
    """
    To Add app data directly, Admin only access
    :param request:
    :return: HTML render, subject_query, username
    """
    username = check_user_logged(request)
    subject = Subject.objects.all()
    new_subject = ""
    return render(request, 'app/add.html', {'subject': subject, 'new_subject': new_subject, 'username': username})


@login_required(login_url='login_view')
@staff_member_required
def add_topic(request):
    """
    Admin only, used to insert a app Topic
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
            subject_id = Subject.objects.get(**{"subject_id": row[7]})
            topic_id = Topic.objects.get(**{"topic_id": row[8]})
            to_insert = {
                # "q_id": row[0],
                "q_text": row[0],
                "a": row[1],
                "b": row[2],
                "c": row[3],
                "d": row[4],
                "e": row[5],
                "answer": row[6],
                "subject_id": subject_id,
                "topic_id": topic_id
            }

            if insert_record(data=to_insert, o="question"):
                row_count = row_count + 1

        return HttpResponse("done")


@login_required(login_url='login_view')
@staff_member_required
def insert_notifications(request):
    file = request.FILES['fileup']
    rows = []
    if file.name.endswith(".csv"):
        data = csv.reader(codecs.iterdecode(file, 'utf-8'))
        for row in data:
            try:
                Notifications.objects.create(notification=row[0])
            except:
                pass
    return HttpResponse('done')


@login_required(login_url='login_view')
@staff_member_required
def add_sub(request):
    """
    adding a app subject
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
    return render(request, 'app/add.html', {'subject': subject, 'new_subject': new_subject})


def test_result(request):
    """
    This views does:
            1, calculate score with calculate function
            2.
    :param request:post request
    :return: Result
    """
    request_data = request.POST.copy()
    data = dict(request_data.items())
    if 'csrfmiddlewaretoken' in data.keys():
        del data['csrfmiddlewaretoken']
    questions = data.pop('question')
    test_obj = TestRecord.objects.get(pk=data.pop('test_obj'))
    d = dict(data)
    answer_list = []
    for k, v in d.items():
        answer_list.append((k, v))
    result = calculator(answer_list, test_obj)
    # return HttpResponse(result)
    return render(request, 'app/test_result.html', {'result': result, 'test_id': test_obj.id, 'username': check_user_logged(request)})


def export_csv(request):
    """
    Export Data as CSV
    :param request:
    :return:
    """
    test_id = request.GET.get('test_id')

    question = []
    try:
        test_obj = TestRecord.objects.get(test_id=test_id)
        test_questions = TestQuestions.objects.filter(test=test_obj)

        for tq in test_questions:
            q = tq.question_id
            question.append(q)
    except:
        pass
    response = HttpResponse(content_type='text/csv')
    response['Content_Disposition'] = 'attachment; filename="answer.csv"'
    writer = csv.writer(response)
    writer.writerow(["q_text", "a", "b", "c", "d", "answer"])

    for item in question:
        writer.writerow([item.q_text, item.a, item.b, item.c, item.d, item.answer])

    return response


def export_questions_as_pdf(request):
    """
    :param request: request
    :return: file as HttpResponse
    """

    test_id = request.GET.get('test_id')

    filename = write_test_to_pdf(test_id)

    with open(filename, 'rb') as pdf:
        pdf = pdf.read()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="my_pdf.pdf"'
        return response



def login_view(request):
    return render(request, 'app/login_page.html')


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
                sess.set_expiry(9000)

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
            extended_user = ExtendedUser.objects.create(user=s)

            json_response = {'if_success': 1, 'comment': str(s)}
    except Exception as e:
        json_response = {'if_success': 0, 'comment': str(e)}
    return JsonResponse(json_response)


def full_test(request):
    print('fthere')
    username = check_user_logged(request)
    subject_name = request.POST.get('Subject')
    sub_obj = Subject.objects.get(subject_name= subject_name)
    subject_id = sub_obj.subject_id

    question_set, test_id = set_maker_for_subject(subject_id)


    if question_set == 'questions less that 30':
        return HttpResponse('Could not create your test, Please go to home page')
    else:
        return render(request, 'app/test.html', {'username': username, 'set': question_set, 'subject': subject_name, 'test_id': test_id})


def full_test_result_calculator(request):
    request_data = request.POST.copy()
    data = dict(request_data.items())
    if 'csrfmiddlewaretoken' in data.keys():
        del data['csrfmiddlewaretoken']
    data.pop('question')
    data.pop('subject')
    test_obj = TestRecord.objects.get(pk=data.pop('test_id'))
    d = dict(data)
    answer_list = []
    for k, v in d.items():
        answer_list.append((k, v))
    result = calculator(answer_list, test_obj)
    calculator(answer_list=None, test_obj=None)
    return JsonResponse(result, safe=False)


def user_analysis(request):
    user = check_user_logged(request)
    detail = analysis(user)
    return render(request, 'app/user_analy.html', {
                                                    'username': user,
                                                    'detail': detail[0],
                                                    'sub_list': detail[1],
                                                    })


@login_required(login_url='login_view')
def user_analysis_new(request):
    user = check_user_logged(request)
    return render(request, 'app/user_analysis.html', {'username': user})


@login_required(login_url='login_view')
def user_profile(request):
    user = check_user_logged(request)
    verified = 'not_verified'
    if not user == 'guest':
        extended_user_obj = ExtendedUser.objects.get(user=User.objects.get(username=user))
        if extended_user_obj.is_verified:
            verified = 'verified'
    return render(request, 'app/profile.html', {'username': user,
                                                'verified': verified,
                                                })


@login_required(login_url='login_view')
def verify(request):
    user = check_user_logged(request)
    if request.method == 'POST':
        otp = request.POST.get('otp')
        verification = otp_verification(username=user, otp=otp)
        return render(request, 'app/profile.html', {'verified': verification, 'username': user})

    if request.method == 'GET':
        otp_creation(username=user)
        return render(request, 'app/profile.html', {'verified': 'otp_sent',
                                                    'username': user,
                                                    'attempt': 1
                                                    })


@login_required(login_url='login_view')
def get_overall_details_for_user_analysis(request):
    username = request.POST.get('username')
    total_questions, attempted, correct, accuracy = overall_details(username)
    data = {
                'total_questions': str(total_questions),
                'attempted': str(attempted),
                'correct': str(correct),
                'accuracy': str(accuracy)
                }
    return JsonResponse(data)


@login_required(login_url='login_view')
def get_subjects_for_user_analysis(request):
    username = request.POST.get('username')

    subject_list = get_subject_list(username)
    return JsonResponse({'data': subject_list})


@login_required(login_url='login_view')
def get_subject_details_for_user_analysis(request):
    username = request.POST.get('username')
    subject_id = request.POST.get('subject')
    total_questions, attempted, correct, accuracy = subject_details(username, subject_id)
    data = {
        'total_questions': str(total_questions),
        'attempted': str(attempted),
        'correct': str(correct),
        'accuracy': str(accuracy)
    }
    return JsonResponse({subject_id: data})


@login_required(login_url='login_view')
def get_topics_for_user_analysis(request):
    username = request.POST.get('username')
    subject = request.POST.get('subject')
    topics = topics_user_analysis(username, subject)
    return JsonResponse({'data': topics})


@login_required(login_url='login_view')
def get_topics_details_for_user_analysis(request):
    username = request.POST.get('username')
    subject_id = request.POST.get('subject')
    topic = request.POST.get('topic')
    topic_data = topic_details(username, subject_id, topic)
    return JsonResponse({'data': topic_data})


class ErrorView(View):
    """
    Generic View for Errors,
        To customize, Go to urls.py , create app url with variable "error_name" inside
        e.g. => path('your_error_url', views.ErrorView.as_view(error_name="error 402"), name='your_error_url'),
    """
    error_name = "Oops! some error"

    def get(self, request, *args, **kwargs):
        return render(request, 'app/error_page.html', {'error': self.error_name})


def error_404(request, exception):
    return render(request, 'app/error_page.html', {'error': "Error 404"})


def error_500(request):
    return render(request, 'app/error_page.html', {'error': "Error 500"})


# not using this currently
@login_required(login_url='login_view')
def set_otp(request):
    username = request.GET.get('username')
    user = User.objects.get(username=username)
    if ExtendedUser.objects.get(user=user).is_verified:
        return HttpResponse('verified')
    else:
        if otp_creation(username=username):
            return HttpResponse('otp created')


# not using this currently
@login_required(login_url='login_view')
def verify_otp(request):
    username = request.GET.get('username')
    otp = request.GET.get('otp')
    return HttpResponse(otp_verification(username=username, otp=otp))


def create_test_view(request):
    """
    returns random questions for a Practice session

    :param request:
    :return: HTML render
    """
    subject, topicname, test_type = None, None, None
    data = dict(request.POST.items())
    print(data)
    if 'Subject' in data.keys():
        subject = data['Subject']
    if 'topicname' in data.keys():
        topicname = data['topicname']
    if 'test_type' in data.keys():
        test_type = data['test_type']

    del data['csrfmiddlewaretoken']
    test_id, questions = create_test(data)
    data = {'subject': subject, 'topic': topicname, 'test_id': test_id, 'questions': questions, 'test_type': test_type}
    return render(request, 'app/show_test.html', data)


def get_result(request):
    data = dict(request.POST.items())
    del data['csrfmiddlewaretoken']

    test_type = data.pop('test_type')
    test_id = data.pop('test_id')

    result = check_result(data, test_type, test_id)
    result['test_id'] = test_id
    return JsonResponse(result)


def get_test_details(request):
    test_id = request.GET.get('test_id')
    test_detail = test_details(test_id)
    return JsonResponse(test_detail)
