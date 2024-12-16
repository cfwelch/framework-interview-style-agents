

import datetime, hashlib, json, re, pytz, os
from django.db import connection, transaction
from django.utils import timezone
from collections import defaultdict
import string
import numpy as np
from nltk.corpus import stopwords
from nltk import word_tokenize
from . import agent

# nltk.download('stopwords')
NAME_LENGTH_LIMIT = 64
FEEDBACK_LENGTH_LIMIT = 5000
PROLIFIC_CODE = ['106C5281']

def isanint(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

def make_prolific_entry(session, user_id, topic):
    ses = session['SESSION_ID'] if 'SESSION_ID' in session else ''
    pro = session['PROLIFIC_PID'] if 'PROLIFIC_PID' in session else ''
    stu = session['STUDY_ID'] if 'STUDY_ID' in session else ''

    add_code_sql = 'INSERT INTO user_extra (user_id, display_name, session_id, prolific_id, study_id) VALUES (%s,%s,%s,%s,%s)'
    with connection.cursor() as cursor:
        cursor.execute(add_code_sql, (user_id, PROLIFIC_CODE[0], ses, pro, stu))
        transaction.commit()
    return PROLIFIC_CODE[0]

# def make_unique_id(inp, user_id):
#     now = datetime.datetime.now()
#     instr = inp[:10] + str(now)
#     code = hashlib.md5(instr.encode()).hexdigest()

#     add_code_sql = 'INSERT INTO user_extra (user_id,display_name) VALUES (%s,%s)'
#     with connection.cursor() as cursor:
#         cursor.execute(add_code_sql, (user_id, code))
#         transaction.commit()
#     return code

def extract_name(name):
    rname = name
    t = re.search('[cC][aA][lL][lL] [mM][eE] (.*)', name)
    if t:
        rname = t.groups()[0]
    t = re.search('[iI] [aA][Mm] (.*)', name)
    if t:
        rname = t.groups()[0]
    t = re.search('[gG][oO] [bB][yY] (.*)', name)
    if t:
        rname = t.groups()[0]
    t = re.search('[iI]\'[mM] (.*)', name)
    if t:
        rname = t.groups()[0]
    return rname

def add_interaction(user_id):
    add_int_sql = 'INSERT INTO interactions (user_id, started) VALUES (%s, %s)'
    with connection.cursor() as cursor:
        cursor.execute(add_int_sql, [user_id, timezone.now()])
        transaction.commit()
        cid = cursor.lastrowid
    return cid

def get_interactions(user_id):
    get_interactions_sql = 'SELECT A.id, A.started, B.word_count, B.time, B.topic FROM interactions AS A JOIN summary AS B ON A.id=B.int_id WHERE A.user_id=%s ORDER BY started DESC'
    with connection.cursor() as cursor:
        cursor.execute(get_interactions_sql, [user_id])
        rows = cursor.fetchall()

    sum_set = []
    for row in rows:
        sum_set.append({'int_id': row[0], 'started': row[1], 'word_count': row[2], 'minutes': '{:.1f}'.format(row[3] / 60.0), 'time': row[3], 'topic': TOPIC_NAMES[row[4]], 'icon': TOPIC_ICONS[row[4]]})
    return sum_set

def add_response(question, response, categories, session_id, time, word_count, topic, interview_id):
    add_response_sql = 'INSERT INTO chat (session_id, question, response, timestamp, time, word_count, topic, interview_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'

    with connection.cursor() as cursor:
        cursor.execute(add_response_sql, (session_id, ','.join(question), response, timezone.now(), time, word_count, topic, interview_id))
        transaction.commit()
        cid = cursor.lastrowid

    add_categories_sql = 'INSERT INTO category (name, count, chat_id) VALUES (%s, %s, %s)'
    with connection.cursor() as cursor:
        insert_values = [(cat, count, cid) for cat, count in categories.items()]
        cursor.executemany(add_categories_sql, insert_values)
        transaction.commit()

def get_questions(session_id, topic, logic):
    get_questions_sql = 'SELECT question FROM chat WHERE session_id=%s AND topic=%s'

    params = [session_id, topic]
    with connection.cursor() as cursor:
        cursor.execute(get_questions_sql, params)
        rows = cursor.fetchall()
    qset = []
    for row in rows:
        qset.extend(row[0].split(','))

    for index, entry in enumerate(qset):
        if 'main_' in entry:
            for key, questionSaved in logic[topic]['questions'].items():
                if str(questionSaved['id']) == str(entry.replace('main_', '')):
                    qset[index] = key
    return qset

def get_survey_questions(topic_id, intro):
    inorout = 'intro=1' if intro else 'outro=1'
    query = 'SELECT id, type, text FROM interview.management_survey WHERE topic=%s AND ' + inorout

    with connection.cursor() as cursor:
        cursor.execute(query, [topic_id])
        rows = cursor.fetchall()

    num_options = {q['value']: q['num_options'] for q in agent.get_question_types()}

    questions = []
    for row in rows:
        questions.append({'id': row[0], 'type': row[1], 'text': row[2], 'num_options': num_options[row[1]]})
    return questions

# def delete_all_chat(user_id):
#     delete_all_chat_sql = 'DELETE FROM chat WHERE user_id=' + str(user_id)
#     with connection.cursor() as cursor:
#         cursor.execute(delete_all_chat_sql)
#         transaction.commit()

def get_survey_status(session_id):
    get_survey_status_sql = """
        SELECT B.text, A.answer, A.before_writing, B.id, B.type
        FROM interview.survey AS A
        JOIN management_survey AS B ON A.question_id=B.id
        WHERE session_id=%s
        """

    params = [session_id]
    with connection.cursor() as cursor:
        cursor.execute(get_survey_status_sql, params)
        rows = cursor.fetchall()
        
    bws = False
    aws = False

    questions = []
    for row in rows:
        if row[2] == 1:
            bws = True
        elif row[2] == 0:
            aws = True
        questions.append({'id': row[3], 'text': row[0], 'answer': row[1], 'before_writing': row[2], 'type': row[4]})
    
    return bws, aws, questions

def submit_survey(answers, before_writing, session_id, topic):
    value_str = ','.join(['(%s, CURRENT_DATE, %s, %s, %s, %s)'] * len(answers))
    submit_survey_sql = 'INSERT INTO interview.survey (session_id, date, before_writing, topic_id, question_id, answer) VALUES ' + value_str
    
    ivals = []
    for qk in answers:
        ivals.extend([session_id, before_writing, topic, qk, answers[qk]])
    
    with connection.cursor() as cursor:
        cursor.execute(submit_survey_sql, ivals)
        transaction.commit()

def submit_feedback(session_id, clarity, summary, features, other):
    clarity = clarity[:FEEDBACK_LENGTH_LIMIT]
    summary = summary[:FEEDBACK_LENGTH_LIMIT]
    features = features[:FEEDBACK_LENGTH_LIMIT]
    other = other[:FEEDBACK_LENGTH_LIMIT]
    submit_feedback_sql = 'INSERT INTO feedback (session_id,date,clarity,summary,features,other) VALUES (%s,%s,%s,%s,%s,%s)'
    with connection.cursor() as cursor:
        cursor.execute(submit_feedback_sql, (session_id, timezone.now(), clarity, summary, features, other))
        transaction.commit()

def filter_name(name):
    fname = name
    return fname[:NAME_LENGTH_LIMIT]

def add_summary(session_id, categories, total_time, total_words, topic):
    add_summary_sql = 'INSERT INTO summary (session_id,timestamp,time,word_count,topic) VALUES (%s,%s,%s,%s,%s)'
    with connection.cursor() as cursor:
        cursor.execute(add_summary_sql, (session_id, timezone.now(), total_time, total_words, topic))
        transaction.commit()
        cid = cursor.lastrowid

    add_categories_sql = 'INSERT INTO category (name, count, summary_id) VALUES (%s, %s, %s)'
    with connection.cursor() as cursor:
        insert_values = [(cat, count, cid) for cat, count in categories.items()]
        cursor.executemany(add_categories_sql, insert_values)
        transaction.commit()

# TODO: Make a more generic survey's query that accepts a dictionary for columns and returns a dictionary
def get_recent_user_surveys(last_timestamp, number_ppl, topic):
    get_recent_user_surveys_sql = 'SELECT q_organoids, q_organoids_favor, q_organoids_favor_after FROM survey WHERE topic_id=%s AND date<=DATE(%s) AND before_writing=0 ORDER BY date DESC LIMIT 0,' + str(number_ppl)
    with connection.cursor() as cursor:
        cursor.execute(get_recent_user_surveys_sql, (topic, last_timestamp))
        rows = cursor.fetchall()

    q_organoids = []
    q_organoids_favor = []
    q_organoids_favor_after = []
    for row in rows:
        q_organoids.append(row[0])
        q_organoids_favor.append(row[1])
        q_organoids_favor_after.append(row[2])

    return q_organoids, q_organoids_favor, q_organoids_favor_after

def get_recent_user_summaries(last_timestamp, number_ppl, topic):
    get_recent_user_summaries_sql = 'SELECT anger,anxiety,sadness,posemo,negemo,work,money,home,health,body,ingest,death,religion,leisure,sexual,joy,fear,i,we,otherpronoun,time,word_count,`order`,justice,purpose FROM summary WHERE topic=%s AND timestamp<%s ORDER BY timestamp DESC LIMIT 0,' + str(number_ppl)
    # with connection.cursor() as cursor:
    #     cursor.execute(get_recent_user_summaries_sql, (topic, last_timestamp))
    #     rows = cursor.fetchall()

    emos = defaultdict(lambda: [])
    topics = defaultdict(lambda: [])
    pronouns = defaultdict(lambda: [])
    total_words = []
    total_time = 0
    total_summaries = 0

    # print(get_recent_user_summaries_sql)
    # print(len(rows))

    # for row in rows:
    for i in range(0, 100):
        total_summaries += 1
        emos['ANGER'].append(5)
        emos['ANX'].append(5)
        emos['SAD'].append(5)
        emos['POSEMO'].append(5)
        emos['NEGEMO'].append(5)
        topics['WORK'].append(5)
        topics['MONEY'].append(5)
        topics['HOME'].append(5)
        topics['HEALTH'].append(5)
        topics['BODY'].append(5)
        topics['INGEST'].append(5)
        topics['DEATH'].append(5)
        topics['RELIG'].append(5)
        topics['LEISURE'].append(5)
        topics['SEXUAL'].append(5)
        topics['ORDER'].append(5)
        topics['JUSTICE'].append(5)
        topics['PURPOSE'].append(5)
        emos['JOY'].append(5)
        emos['FEAR'].append(5)
        pronouns['I'].append(5)
        pronouns['WE'].append(5)
        pronouns['OTHER'].append(5)
        total_time += 5
        total_words.append(5)

    return emos, topics, pronouns, total_time, total_words, total_summaries

# Session ID is separate from session because we want the admin to be able to pass a key that isn't from the current session.
def get_stats(session, topic, session_id):
    get_stats_sql = 'SELECT A.id, question, response, time, word_count, timestamp, name, count, interview_id FROM chat AS A LEFT OUTER JOIN category AS B ON A.id=B.chat_id WHERE session_id=%s AND topic=%s ORDER BY timestamp ASC'

    params = [session_id, topic]

    with connection.cursor() as cursor:
        cursor.execute(get_stats_sql, params)
        rows = cursor.fetchall()
    categories = defaultdict(lambda: 0)
    convo = []
    qset = []
    all_times = []
    last_ppid = 0
    last_timestamp = None
    total_words = 0
    previous_chat_id = -1
    interview_id = None
    for row in rows:
        interview_id = row[8]
        if previous_chat_id != row[0]:
            sysparts = row[1].split(',')
            convo.append({'agent': True, 'name': None, 'text': sysparts})
            convo.append({'agent': False, 'name': 'You', 'text': row[2]})
            last_ppid = sysparts[-1] # TODO: is this a bug? Should it be just sysparts?
            last_timestamp = row[5]
            all_times.append(int(row[3]) if isanint(row[3]) else 0)
            qset.extend(sysparts)
            total_words += row[4]
        if row[6] != None:
            categories[row[6]] += row[7]
        previous_chat_id = row[0]
    return categories, convo, qset, last_ppid, all_times, total_words, last_timestamp, interview_id

# If you call this function without an interview_id, it sets the session interview logic to the current active interview for that topic.
# If you pass an interview_id, it will set the logic to the logic from that specific version, e.g. when viewing a summary from an older interview version.
def set_active_interview(topic, session, interview_id=None):
    end_cond = 'A.active=1' if interview_id == None else 'A.id=' + str(interview_id)
    set_active_interview_sql = 'SELECT A.id,respect_order, question, question_order, B.interview_id, C.cpname FROM interview.management_interview AS A JOIN interview.management_question AS B on A.id=B.interview_id JOIN interview.management_topics AS C ON A.topic_id = C.id WHERE B.topic_id=%s AND ' + end_cond
    with connection.cursor() as cursor:
        cursor.execute(set_active_interview_sql, [topic])
        rows = cursor.fetchall()

    if 'logic' not in session:
        session['logic'] = {}

    counter = 0
    for row in rows:
        if counter == 0:
            # Create map for the topic, question order, number of questions and map
            session['logic'][topic] = {}
            session['logic'][topic]['name'] = row[5]
            session['logic'][topic]['respect_order'] = row[1] == 1
            session['logic'][topic]['number_main_q'] = len(rows)
            session['logic'][topic]['questions'] = {}
            session['interview_id'] = row[4]
        session['logic'][topic]['questions']['q' + str(row[3])] = {'id': 'main_q' + str(row[3]), 'question': row[2], 'db_id': row[0]}
        counter += 1

    set_active_reflections_sql = 'SELECT A.id, B.reflection, B.conditions, B.interview_id FROM interview.management_interview AS A JOIN interview.management_reflection AS B on A.id=B.interview_id WHERE A.topic_id=%s AND ' + end_cond
    with connection.cursor() as cursor:
        cursor.execute(set_active_reflections_sql, [topic])
        rows = cursor.fetchall()

    session['logic'][topic]['reflections'] = {}
    for row in rows:
        session['logic'][topic]['reflections']['reflection_' + str(row[3])] = {'reflection': row[1], 'conditions': json.loads(row[2])}

def clean_text(text):
    stop_words = set(stopwords.words('english'))
    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))
    
    # Convert to lowercase
    text = text.lower()
    text = ' '.join([word for word in text.split() if word not in stop_words])

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def get_values(msg, topic):
    get_topic_lexicon_sql = 'SELECT word, A.category FROM interview.management_lexicon AS A JOIN interview.management_lexicon_topic AS B ON B.category=A.category WHERE B.topic=%s'
    with connection.cursor() as cursor:
        cursor.execute(get_topic_lexicon_sql, [topic])
        rows = cursor.fetchall()

    lexicon_map = {}
    for row in rows:
        if row[1] not in lexicon_map:
            lexicon_map[row[1]] = set()
        lexicon_map[row[1]].add(row[0])

    tokens = preprocess(msg)

    lparts = []
    for t in tokens:
        for category, words in lexicon_map.items():
            if check_liwc(t, words):
                lparts.append(category)

    categories = defaultdict(lambda: 0)
    for lp in lparts:
        categories[lp] += 1

    return tokens, categories

def preprocess(sentence):
    return [i.lower() for i in word_tokenize(sentence)]

def check_liwc(token, category):
    for stem in category:
        if('*' in stem):
            stem = stem.replace('*', '')
            if token[:len(stem)] == stem:
                return True
        else:
            if stem == token:
                return True
    return False
