import csv


def get_the_data(username):
    flag = 0
    subject_dict = {}

    # entering the subject names in the dict
    with open('/home/abhinav/PycharmProjects/more/TheGkApp/records/test_record.csv', 'r') as file:
        reader = csv.reader(file)
        for r in reader:
            #             print(r)
            if flag == 0:
                print(r)
                flag = 1
                continue
            sub = r[3]
            if not sub in subject_dict.keys():
                subject_dict[sub] = {}
        file.close()

    # entering the topic names
    with open('/home/abhinav/PycharmProjects/more/TheGkApp/records/test_record.csv', 'r') as file:
        reader = csv.reader(file)
        for r in reader:
            if flag == 0:
                flag = 1
                continue
            sub = r[3]
            if sub in subject_dict.keys():
                #                 print('yes it is in key ',sub)
                if not r[4] in subject_dict[sub].keys():
                    subject_dict[sub][r[4]] = []

    with open('/home/abhinav/PycharmProjects/more/TheGkApp/records/test_record.csv', 'r') as file:
        reader = csv.reader(file)
        for r in reader:
            if flag == 0:
                flag = 1
                continue
            if r[3] in subject_dict.keys():
                if r[4] in subject_dict[r[3]].keys():
                    if subject_dict[r[3]][r[4]] == []:
                        #                         print('ist append in ',[r[4]])
                        subject_dict[r[3]][r[4]] = [int(r[5]), int(r[6]), int(r[7]), int(r[8]), int(r[9]), float(r[10])]
                    else:
                        #                         print('next append in',r[4])
                        subject_dict[r[3]][r[4]][0] += int(r[5])
                        subject_dict[r[3]][r[4]][1] += int(r[6])
                        subject_dict[r[3]][r[4]][2] += int(r[7])
                        subject_dict[r[3]][r[4]][3] += int(r[8])
                        subject_dict[r[3]][r[4]][4] += int(r[9])
                        subject_dict[r[3]][r[4]][5] += float(r[10])
    return subject_dict


data = get_the_data('abhinav')
analyse_list = []


def set_the_data(data):
    for subject, sub_data in data.items():
        sub_analyse_list = []
        for topic, topic_data in sub_data.items():
            # topic, ques_asked, ques_attempted, ques_correct, accuracy(float), score
            sub_analyse = [topic, topic_data[0], topic_data[1], topic_data[2], float(topic_data[2] / topic_data[1]),
                           topic_data[5]]
            sub_analyse_list.append(sub_analyse)
        analyse_list.append((subject, sub_analyse_list))
    print(analyse_list)


set_the_data(data)