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








