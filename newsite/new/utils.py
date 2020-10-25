from random import choice
from .models import Subject, Topic, Questions
from string import ascii_uppercase, digits
import random
import pandas as pd
import operator
import csv
from .mail import send_otp_mail
from django.contrib.auth.models import User
import os


MODEL_OBJ = {
    "sub": Subject,
    "topic": Topic,
    "question": Questions,
}


# prefix should be three characters of subject. like for Physics
def id_generator(o, prefix="PHY"):
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
        pid = id_generator(prefix, o)
        return pid


def insert_record(data, o):
    obj = MODEL_OBJ[o]
    try:
        o1, c = obj.objects.get_or_create(**data)
    except Exception as e:
        print(str(e))
        return None
    return c


def set_maker():

    topic = Topic.objects.all().filter(**{'topic_id': 'TOPCYZ93HK'})
    print(len(topic))
    print(topic)
    for i in topic:
        question = Questions.objects.filter(**{'topic_id':i})

    q = random.choices(question, k=10)
    return q


def set_maker1(topic_id):

    topic = Topic.objects.all().filter(**{'topic_id':topic_id })
    print(len(topic))
    print(topic)
    for i in topic:
        question = Questions.objects.filter(**{'topic_id':i})

    try:
        q = random.choices(question, k=10)
    except:
        q = []
    return q


def set_maker_for_subject(subject_id):
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
                q_list.append({'q_id': question.q_id,
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

    data = pd.read_csv('records/test_record.csv')

    print(data.head(3))
    userwise = data.groupby('username')

    for uname, user_data in userwise:

        if uname == user:
            user_subject_wise = user_data.groupby('subject')
        else:
            return 'no data'
    sub_wise_dict = {}
    print(sub_wise_dict)

    html_table = {}
    for sub, sub_data in user_subject_wise:
        topic_data = sub_data.groupby('topic')
        html_table[sub] = sub_data.groupby('topic').sum().to_html()
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
    print(sorted_list)

    return sorted_list, sub_wise_dict.keys(), html_table


def otp_generator(user):
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
    attempt = -1
    write_again = []
    with open('records/otp.csv', 'r+') as file:
        reader = csv.reader(file)
        print(type(reader))
        for r in reader:
            print(type(r))
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




def analyse(user):
    if user == '':
        return '<h1>Please Login</h1>'
    df = pd.read_csv('records/test_record.csv')

    grouped = df.groupby('username')
    if user not in grouped.groups.keys():
        return '<h1> Hi' + user + ', It seems you do not have practiced any test yet</h1>'
    for user_name, data in grouped:
        subject_wise = []
        if user_name == user:
            #         print(data)
            sub_group = data.groupby('subject')

            sub_group = dict(tuple(sub_group))

    plot = {}
    tag = ''
    for k, v in sub_group.items():
        v.set_index('topic', inplace=True)

        v.drop(v.columns[[0, 1, 2, 3]], axis=1, inplace=True)

        plot[k] = v.groupby('topic').sum().plot(kind='bar', figsize=(10, 8))
        plot[k].set_xticklabels(v.index, rotation=20)
        print(v.groupby('topic').sum())
        image = plot[k].get_figure().savefig("new/static/new/images/"+user + '_' + k + '.png')
        css = '<style>  body {text-align:center;\n} \ntable\n{margin:0px auto;\n}  </style>'
        heading = '<h2> Subject : ' + k + '</h2>'
        table = v.groupby('topic').sum().to_html()

        html = ' <div class="image">  <img src = "{% static "new/images/" + user + "_" + k + ".png" + " >  </div>'
        tag = tag+css+heading+table+html
    return str(tag)
