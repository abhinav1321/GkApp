from random import choice
from .models import Subject, Topic, Questions
from string import ascii_uppercase, digits
import random
import pandas as pd
from .mail import send_otp_mail
from django.contrib.auth.models import User
from .models import ExtendedUser, TestRecord, TestQuestions, OtpRegistration
import pdfkit



MODEL_OBJ = {
    "sub": Subject,
    "topic": Topic,
    "question": Questions,
}


# prefix should be three charactors of subject. like for Physics
def id_generator(o, prefix="PHY"):
    """
    To create random ID for subject or topic
    :param o: Model Object name, can be sub or topic
    :param prefix: refix should be three charactors of subject. like for Physics
    :return: it will return created ID
    """
    obj = MODEL_OBJ[o]
    pid = prefix + ''.join(choice(ascii_uppercase + digits) for _ in range(6))
    try:
        if o == "sub":
            obj.objects.get(subject_id=pid)
        if o == "topic":
            obj.objects.get(topic_id=pid)
    except (KeyError, obj.DoesNotExist):
        return pid
    else:
        pid = id_generator(o, prefix)
        return pid


def insert_record(data, o):
    """
    To insert record,common for sub, object or question
    :param data: data to be inserted
    :param o: name of the object, (sub/question/topic)
    :return: variable c (created) , True/False
    """
    obj = MODEL_OBJ[o]
    print(obj, 'if ques')
    c = False
    try:
        if o == 'question':
            object = obj.objects.create(**data)
            print(object, 'object')
        else:
            o1, c = obj.objects.get_or_create(**data)
            print(o1, c)
    except Exception as e:
        return None
    return c


def set_maker(topic_id):
    """
    needs topic id to create a question set
    :param topic_id: topic_id
    :return: set of randomised questions
    """
    topic = Topic.objects.all().filter(**{'topic_id': topic_id})
    for i in topic:
        question = Questions.objects.filter(**{'topic_id': i})
    q = random.choices(question, k=10)
    return q


def calculator(answer_list=None, test_obj=None):
    """

    :param answer_list:
    :param test_obj:
    :return:
    """
    count = 0
    for answer in answer_list:
        question_id, response = answer[0], answer[1]
        try:
            correct_or_incorrect = False
            obj = Questions.objects.filter(**{"q_id": question_id})[0]
            if response.lower() == obj.answer.lower():
                correct_or_incorrect = True
                count += 1
            if test_obj:
                test_question_obj = TestQuestions.objects.filter(test=test_obj, question_id=obj)
                test_question_obj.update(correct_or_incorrect=correct_or_incorrect, attempted=True)

        except Exception as e:
            print(e)
    return count


def set_maker_for_subject(subject_id):
    """
    Making set of 30 questions for a subject Quiz
    :param subject_id: subject_id
    :return: set of 30 questions, a final_list
    """
    q_set = []
    q_list = []
    sum = 0
    topic = Topic.objects.filter(subject_id=Subject.objects.filter(subject_id=subject_id)[0])
    for t in topic:
        question_set = Questions.objects.filter(topic_id=Topic.objects.filter(topic_id=t.topic_id)[0])
        if len(question_set) > 0:
            q_set.append((question_set, t.topic_id, len(question_set)))
    for q in q_set:
        sum = sum + (q[2])
    if sum > 30:
        for q_item in q_set:
            for question in q_item[0]:
                q_list.append({
                                'q_id': question.q_id,
                                'q_text': question.q_text,
                                'a': question.a,
                                'b': question.b,
                                'c': question.c,
                                'd': question.d,
                                'e': question.e,
                                'rich': question.q_rich,
                                'answer': question.answer,
                                'topic': q_item[1]})

        final_list = random.choices(q_list, k=30)
    else:
        final_list = 'questions less that 30'
    return final_list


def analysis(user):
    user_obj = User.objects.get(username=user)
    extended_user_obj = ExtendedUser.objects.get(user=user_obj)
    small_tests = TestRecord.objects.filter(user=extended_user_obj, test_type='S')
    full_tests = TestRecord.objects.filter(user=extended_user_obj, test_type='F')
    df = pd.DataFrame(list(small_tests.values()))

    subjects = df.subject_id.unique()
    topics = df.topic_id.unique()

    subject_replace = []
    for subject in subjects:
        sub_obj = Subject.objects.get(pk=subject)
        subject_replace.append(sub_obj.subject_name)
    df['subject_name'] = df['subject_id'].replace(list(subjects), subject_replace)

    topic_replace = []
    for topic in topics:
        topic_obj = Topic.objects.get(pk=topic)
        topic_replace.append(topic_obj.topicname)
    df['topic_name'] = df['topic_id'].replace(list(topics), topic_replace)

    df['user_id'] = user
    df['test_type'] = 'Short'

    new_data = []
    for test_id in list(df.id):
        test_obj = TestRecord.objects.get(pk=test_id)
        total_questions = len(TestQuestions.objects.filter(test=test_obj))
        attempted = len(TestQuestions.objects.filter(test=test_obj, attempted=True))
        correct = len(TestQuestions.objects.filter(test=test_obj, correct_or_incorrect=True))
        new_data.append([total_questions, attempted, correct])
    extra_data = pd.DataFrame(new_data,
                              columns=['total_questions', 'attempted', 'correct'])
    new_df = pd.concat([df, extra_data], axis=1)
    return new_df


def record_questions_in_test_record(test_obj, question_list):
    """

        :param test_obj: obj of TestRecord model
        :param question_list: a list of Dicts,
                          Example:  [{"q_id": 1}]

        :return: No return
        """
    for question in question_list:
        try:
            question_object = Questions.objects.get(id=question['q_id'])
            tq_obj = TestQuestions.objects.create(test=test_obj, question_id=question_object)

        except Exception as e:
            print(e, 'as b')


def update_question_in_test_record(test_obj, question_list):
    """
    :param test_obj: obj of TestRecord model
    :param question_list: a list of Dicts,
            e.g. : [ {'question_id':1, 'attempted':True, 'correct_or_incorrect':False},{},{},...]
    :return: No return
    """
    for question in question_list:
        try:
            question_object = Questions.objects.get(q_id=question.question_id)
            test_question_object = TestQuestions.objects.get(test=test_obj, question_id=question_object)
            test_question_object.update(attempted=question.attempted, correct_or_incorrect=question.correct_or_incorrect)
            test_question_object.save()
        except Exception as e:
            print('Excption during updation ', e)


def test_record(username, subject, topic, test_type='F'):
    """

    :param username: username
    :param subject: subject obj
    :param topic: topic obj
    :param test_type: 'F' or 'S'
    :return: created test_obj
    """
    test_obj = None
    try:

        if username == '':
            test_obj = TestRecord.objects.create(test_type=test_type,
                                                 subject=subject, topic=topic)
        else:
            user_obj = User.objects.get(username=username)
            obj = ExtendedUser.objects.get(user=user_obj)
            test_obj = TestRecord.objects.create(test_type=test_type,
                                                 user=obj, subject=subject, topic=topic)
        test_obj.save()
    except Exception as e:
        print(e, 'test record Exception')
    return test_obj


def overall_details(username):
    data = analysis(username)
    total_questions = data.sum().total_questions
    attempted = data.sum().attempted
    correct = data.sum().correct
    accuracy = (attempted/correct)*100
    return total_questions, attempted, correct, accuracy


def get_subject_list(username):
    data = analysis(username)
    subject_id_list = list(data.subject_id.unique())
    subject_dict = {}
    for sub_id in subject_id_list:
        sub_obj = Subject.objects.get(pk=sub_id)
        sub_id, sub_name = sub_obj.subject_id, sub_obj.subject_name
        subject_dict[str(sub_id)] = sub_name
    return subject_dict


def topics_user_analysis(username, subject):
    data = analysis(username)
    data = data[data['subject_id'] == subject]
    topics = list(data.topic_id.unique())
    return topics


def subject_details(username, subject_id):
    data = analysis(username)
    data = data[data['subject_id'] == subject_id]
    total_questions = data.sum().total_questions
    attempted = data.sum().attempted
    correct = data.sum().correct
    accuracy = (attempted / correct) if correct>0 else 0
    return total_questions, attempted, correct, accuracy


def topic_details(username, subject_id, topic):
    data = analysis(username)
    data = data[(data['subject_id'] == subject_id) & (data['topic_id'] == topic)]
    total_questions = data.sum().total_questions
    attempted = data.sum().attempted
    correct = data.sum().correct
    accuracy = (correct / attempted) if attempted > 0 else 0
    return total_questions, attempted, correct, accuracy


def get_test_questions(test_obj, number=None):
    test_questions_list = TestQuestions.objects.filter(test=test_obj)
    if number:
        question = list(test_questions_list)[number-1]
        question = question.question_id
        question_dict = {
            'q_id': question.q_id,
            'a': question.a,
            'b': question.b,
            'c': question.c,
            'd': question.d,
            'q_text': question.q_text
        }
        return question_dict
    return test_questions_list


def otp_verification(extended_user_id=None, username=None, otp=None):
    if extended_user_id:
        extended_user_object = ExtendedUser.objects.get(id=extended_user_id)
    if username:
        extended_user_object = ExtendedUser.objects.get(user=User.objects.get(username=username))

    if extended_user_object.is_verified:
        return 'verified'
    else:
        otp_object = OtpRegistration.objects.filter(user=extended_user_object).latest('date')
        if otp_object.otp == otp and otp_object.attempt<=3:
            ExtendedUser.objects.filter(id=extended_user_object.id).update(is_verified=True)
            return 'verified'
        elif otp_object.attempt > 3:
            return 'damage'
        else:
            OtpRegistration.objects.filter(id=otp_object.id).update(attempt=int(otp_object.attempt)+1)

            return 'otp_failed'


def otp_creation(extended_user_id=None, username=None):
    if extended_user_id:
        extended_user_object = ExtendedUser.objects.get(id=extended_user_id)
    if username:

        extended_user_object = ExtendedUser.objects.get(user=User.objects.get(username=username))

    if not extended_user_object.is_verified:
        otp = random.randint(10000, 99999)
        user_email = extended_user_object.user.email
        OtpRegistration.objects.create(user=extended_user_object, otp=otp)
        send_otp_mail(user_email, 'Otp Verification', 'Hi your Otp is ' + str(otp))
        return True


def write_test_to_pdf(test_id):
    """
    :param test_id: test_id : type-string
    :return: pdf file location
    """
    print(test_id, 'test_id')
    test_record_obj = TestRecord.objects.get(pk=test_id)
    test_questions = get_test_questions(test_record_obj)

    html_code = '<div id="Info"> <h1>Test Answers</h1> ' + ' </div>'
    css = '<style> #info{text-align:center;}' \
          ' #question_div{ background-color:#fffdd0; margin:50px;} ' \
          ' #answer_div{padding:50px;} ' \
          ' body{background-color:khaki} </style>'
    i = 0
    for tq_obj in test_questions:
        i += 1
        question_obj = tq_obj.question_id
        question_text = '<h3>' + str(i) + ': ' + question_obj.q_text + '</h3>'
        a = '<p> 1. ' + question_obj.a + '</p>'
        b = '<p> 2. ' + question_obj.b + '</p>'
        c = '<p> 3. ' + question_obj.c + '</p>'
        d = '<p> 4. ' + question_obj.d + '</p>'
        answer = '<h4> Answer: ' + question_obj.answer + '</h4>'
        div = '<div id="question_div"> ' + '<div id="answer_div">' \
              + question_text + a + b + c + d + answer + '</div> ' + '</div>'
        html_code += div
    html_code += css
    with open('records/test_record.html', 'w') as file:
        file.write(html_code)
    pdfkit.from_file('records/test_record.html', 'records/test_record.pdf')
    return 'records/test_record.pdf'
