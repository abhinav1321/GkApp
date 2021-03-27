from random import choice
from .models import Subject, Topic, Questions
from string import ascii_uppercase, digits
import random
import pandas as pd
import operator
import csv
from .mail import send_otp_mail
from django.contrib.auth.models import User
from .models import ExtendedUser, TestRecord, TestQuestions



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
    try:
        o1, c = obj.objects.get_or_create(**data)
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

#
# def set_maker1(topic_id):
#
#     topic = Topic.objects.all().filter(**{'topic_id': topic_id})
#     print(len(topic))
#     for i in topic:
#         question = Questions.objects.filter(**{'topic_id': i})
#
#     try:
#         q = random.choices(question, k=10)
#
#     except:
#         q = []
#     return q


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


def analysis1(user):
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


def analysis(user):
    """
    Analyse the test records for a particular user
    :param user: user_object
    :return: dict of (list_sorted, keys)
    """
    data = pd.read_csv('records/test_record.csv')
    user_wise_data = data.groupby('username')

    for u, u_data in user_wise_data:
        if u == user:
            user_subject_wise = u_data.groupby('subject')
            sub_wise_dict = {}

            for sub, sub_data in user_subject_wise:
                topic_data = sub_data.groupby('topic')
                topic_dict = {}
                for topic_name, top_data in topic_data:
                    topic_dict[topic_name] = top_data.reset_index()
                sub_wise_dict[sub] = topic_dict

            score_list = []
            for k, v in sub_wise_dict.items():

                for key, value in v.items():
                    total_ques_asked = value['ques_asked'].sum()
                    total_ques_attempted = value['ques_attempted'].sum()
                    total_ques_correct = value['ques_correct'].sum()
                    total_ques_incorrect = value['ques_incorrect'].sum()
                    total_ques_unattempted = value['ques_unattempted'].sum()
                    accuracy = total_ques_correct / total_ques_attempted
                    percent_score = value['score_in_the_topic'].sum() / value['score_in_the_topic'].count()

                    score_list.append([k, key,
                                       total_ques_asked,
                                       total_ques_attempted,
                                       total_ques_correct,
                                       total_ques_incorrect,
                                       total_ques_unattempted,
                                       accuracy,
                                       percent_score,
                                       ]
                                      )

            sorted_list = sorted(score_list, key=operator.itemgetter(0, 8))

            return sorted_list, sub_wise_dict.keys()


def otp_generator(user):
    """
    Used to generate OTP
    :param user:user_object
    :return:otp
    """
    with open('records/otp.csv', 'a') as file:
        reader = csv.reader(file)
        writer = csv.writer(file)
        otp = random.randint(10000, 99999)
        # otp entry is a log to get the latest otp
        otp_entry = random.randint(1000, 9999)
        writer.writerow((otp_entry, user, otp, 1))
        user_id = User.objects.get(username=user)
        user_email = user_id.email
        send_otp_mail(user_email, 'Otp Verification', 'Hi your Otp is ' + str(otp))
        return otp_entry


def otp_verifier(otp, otp_entry, user, verified):
    """
    verification of OTP

    :param otp: Actual Otp
    :param otp_entry: EnPered OTp
    :param user: username
    :param verified: 'verified'/'not verified'
    :return: [verified, attempt]
    """
    attempt = -1
    write_again = []
    with open('records/otp.csv', 'r+') as file:
        reader = csv.reader(file)
        for r in reader:
            # print(type(r[0]), type(r[1]), type(r[2]), type(otp_entry), type(otp))
            if r[0] == otp_entry:
                r[3] = int(r[3])+1
                attempt = r[3]

                if r[2] == otp:
                    with open('records/registered_user.csv', 'a') as user_file:
                        writer = csv.writer(user_file)
                        writer.writerow([user])
                        verified = 'verified'
            write_again.append(r)
    with open('records/otp.csv', 'r+') as file:
        rewriter = csv.writer(file)
        for line in write_again:
            rewriter.writerow(line)
    return [verified, attempt]


def record_questions_in_test_record(test_obj, question_list):
    """

        :param test_obj: obj of TestRecord model
        :param question_list: a list of Dicts,
                          Example:  [{"q_id": 1}]

        :return: No return
        """
    for question in question_list:
        try:
            question_object = Questions.objects.get(q_id=question['q_id'])
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
    data = analysis1(username)
    total_questions = data.sum().total_questions
    attempted = data.sum().attempted
    correct = data.sum().correct
    accuracy = (attempted/correct)*100
    return total_questions, attempted, correct, accuracy


def get_subject_list(username):
    data = analysis1(username)
    subject_id_list = list(data.subject_id.unique())
    subject_dict = {}
    for sub_id in subject_id_list:
        print(sub_id)
        sub_obj = Subject.objects.get(pk=sub_id)
        sub_id, sub_name = sub_obj.subject_id, sub_obj.subject_name
        subject_dict[str(sub_id)] = sub_name
    return subject_dict


def topics_user_analysis(username, subject):
    data = analysis1(username)
    data = data[data['subject_id'] == subject]
    topics = list(data.topic_id.unique())
    return topics


def subject_details(username, subject_id):
    data = analysis1(username)
    data = data[data['subject_id'] == subject_id]
    total_questions = data.sum().total_questions
    attempted = data.sum().attempted
    correct = data.sum().correct
    accuracy = (attempted / correct) if correct>0 else 0
    return total_questions, attempted, correct, accuracy


def topic_details(username, subject_id, topic):
    data = analysis1(username)
    data = data[(data['subject_id'] == subject_id) & (data['topic_id'] == topic)]
    total_questions = data.sum().total_questions
    attempted = data.sum().attempted
    correct = data.sum().correct
    accuracy = (correct / attempted) if attempted > 0 else 0
    return total_questions, attempted, correct, accuracy
