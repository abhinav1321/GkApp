from random import choice
from .models import Subject, Topic, Questions
from string import ascii_uppercase, digits
import random


MODEL_OBJ = {
    "sub": Subject,
    "topic": Topic,
    "question": Questions,
}
# prefix should be three charactors of subject. like for Physics
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


    q= random.choices(question,k=10)
    return q



def set_maker1(topic_id):

    topic = Topic.objects.all().filter(**{'topic_id':topic_id })
    print(len(topic))
    print(topic)
    for i in topic:
        question = Questions.objects.filter(**{'topic_id':i})

    try:
        q= random.choices(question,k=10)
    except:
        q=[]
    return q


def set_maker_for_subject(subject_id):
    q_set = []
    q_list=[]
    sum=0
    topic = Topic.objects.filter(subject_id= Subject.objects.filter(subject_id=subject_id)[0])
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



