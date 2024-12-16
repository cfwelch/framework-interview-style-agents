from datetime import datetime
import json, pickle, subprocess, time, math, os, sys, re
from django.db import connection, transaction
import pandas as pd
from write import agent
from ewc19.settings import BASE_DIR, STATIC_ROOT
from write import agent
from fpdf import FPDF
from django.templatetags.static import static
from collections import defaultdict

""""FPDF counstrutor"""
class PDF(FPDF):
     pass # nothing happens when it is executed.

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def create_dictionary(keys, values):
    result = {} # empty dictionary
    for key, value in zip(keys, values):
        result[key] = value
    return result

def seconds_to_displayable(seconds):
    return time.strftime('%H:%M:%S', time.gmtime(math.floor(seconds)))

def get_number_of_chats():
    query = 'SELECT count(*), topic FROM summary GROUP BY topic'
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    interaction_counts = {}
    for row in rows:
        interaction_counts[row[1]] = row[0]

    return interaction_counts

def get_distribution_of_time(topic):
    query = 'SELECT count(*), avg(time) FROM summary WHERE topic=%s'
    with connection.cursor() as cursor:
        cursor.execute(query, [topic])
        rows = cursor.fetchall()

    if rows [0][0] == 0:
            return '00:00:00'

    return seconds_to_displayable(rows[0][1])

def get_all_conversations(topic):
    query = 'SELECT * FROM summary WHERE topic=%s ORDER BY timestamp DESC'
    with connection.cursor() as cursor:
        cursor.execute(query, [topic])
        desc = cursor.description
        
        return [
            dict(zip([col[0] for col in desc], row)) 
            for row in cursor.fetchall() 
        ]

    return rows

def get_average_word_count(topic):
    query = 'SELECT count(*), avg(word_count) FROM summary WHERE topic=%s'
    with connection.cursor() as cursor:
        cursor.execute(query, [topic])
        rows = cursor.fetchall()

    if rows [0][0] == 0:
        return 0

    return math.floor(rows[0][1])

def fix_chartjs_title(title):
    TOO_LONG = 100
    newtitle = title.replace('\'', '"')
    title_chunks = []
    title_words = newtitle.split(' ')
    new_chunk = ''
    for word in title_words:
        if len(new_chunk) + len(word) > TOO_LONG:
            title_chunks.append(new_chunk)
            new_chunk = word
        else:
            if new_chunk != '':
                new_chunk += ' '
            new_chunk += word
    if new_chunk != '':
        title_chunks.append(new_chunk)
    return title_chunks

def get_survey_distribution(topic):
    query_survey = """
        SELECT A.session_id, A.date, A.before_writing, A.question_id, A.answer, B.text, B.type
        FROM interview.survey AS A
        JOIN interview.management_survey AS B ON A.question_ID=B.id
        WHERE topic_id=%s
        """

    with connection.cursor() as cursor:
        cursor.execute(query_survey, [topic])
        rows = cursor.fetchall()

    num_options = {q['value']: q['num_options'] for q in agent.get_question_types()}
    
    question_dict = {}
    for row in rows:
        qid = row[3]
        before_writing = row[2]
        if qid not in question_dict:
            question_dict[qid] = {
                'id': qid, 
                'dates': {0: [], 1: []}, 
                'answers': {
                    0: {i: 0 for i in range(num_options[row[6]])}, 
                    1: {i: 0 for i in range(num_options[row[6]])}
                }, 
                'text': fix_chartjs_title(row[5]), 
                'type': row[6], 
                'num_options': num_options[row[6]],
                'after': False,
                'before': False,
                'labels': [i+1 for i in range(num_options[row[6]])]
            }
        # Index the answers by before_writing (row[2] is 1 if true) or after writing (0)
        question_dict[qid]['answers'][before_writing][row[4]] += 1
        question_dict[qid]['dates'][before_writing].append(row[1])
        if before_writing == 1:
            question_dict[qid]['before'] = True
        else:
            question_dict[qid]['after'] = True

    return question_dict

def get_time_chart_data(topic):
    # Define the bin size in minutes
    bin_size = 2

    # SQL query
    query = "SELECT time FROM summary WHERE topic = %s"

    with connection.cursor() as cursor:
        cursor.execute(query, [topic])
        rows = cursor.fetchall()

    # Initialize data storage
    nb = defaultdict(int)
    avg = defaultdict(int)

    # Loop over the rows to process the data
    max_bin_index = 0
    for row in rows:
        if row[0] is not None:
            # Find the bin for the current row
            bin_index = math.floor(row[0] / (60 * bin_size))
            
            # Update the data for this bin
            avg[bin_index] += row[0]
            nb[bin_index] += 1

            # Update the maximum bin index
            max_bin_index = max(max_bin_index, bin_index)

    # Generate a complete set of bins from 0 to max_bin_index
    for bin_index in range(max_bin_index + 1):
        if bin_index not in nb:
            nb[bin_index] = 0
            avg[bin_index] = 0

    # Calculate the average time and generate labels
    labels = []
    for bin_index in sorted(avg.keys()):
        if nb[bin_index] > 0:
            avg[bin_index] = math.floor(avg[bin_index] / (60 * nb[bin_index]))
        labels.append(f'{bin_index*bin_size}-{(bin_index+1)*bin_size} Minutes')

    # Convert to list in order to maintain order of bins
    nb = [nb[bin_index] for bin_index in sorted(nb.keys())]
    avg = [avg[bin_index] for bin_index in sorted(avg.keys())]

    return {'avg': avg, 'nb': nb, 'labels': labels}

def get_topics(active_only=False):
    aonly = ' LEFT OUTER JOIN interview.management_interview AS B ON A.id=B.topic_id WHERE B.active=1' if active_only else ''
    query = 'SELECT A.id, topic, cpname, iconfile, intro_disclaimer from interview.management_topics AS A' + aonly

    topics = []
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            topic = {'id': row[0], 'name': row[1], 'cpname': row[2], 'file': row[3], 'intro_disclaimer': row[4]}
            topics.append(topic)

    return topics

def get_lexicon_assignments():
    query = """
        SELECT A.id, A.topic, iconfile, B.category
        FROM interview.management_topics AS A
        LEFT OUTER JOIN interview.management_lexicon_topic AS B on B.topic=A.id
        ORDER BY A.id, B.category ASC
        """
    
    topics = []
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        prev_id = -1
        for row in rows:
            if row[0] != prev_id:
                topic = {'id': row[0], 'name': row[1], 'file': row[2], 'categories': []}
                if row[3] != None:
                    topic['categories'].append(row[3])
                topics.append(topic)
            else:
                topics[-1]['categories'].append(row[3])
            prev_id = row[0]

    return topics

def get_valid_lexicons():
    query = "SELECT DISTINCT category FROM interview.management_lexicon"

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        cats = []
        for row in rows:
            cats.append(row[0])

    return cats

def add_lexicon_assignment(topic_id, category):
    query = 'INSERT INTO interview.management_lexicon_topic (category, topic) VALUES (%s, %s)'

    with connection.cursor() as cursor:
        cursor.execute(query, [category, topic_id])
        transaction.commit()

def remove_lexicon_assignment(topic_id, category):
    query = "DELETE FROM interview.management_lexicon_topic WHERE topic=%s and category=%s"

    with connection.cursor() as cursor:
        cursor.execute(query, [topic_id, category])
        transaction.commit()

def get_active_lexicons_for_topic(topic_id):
    query = 'SELECT category FROM interview.management_lexicon_topic WHERE topic=%s'

    with connection.cursor() as cursor:
        cursor.execute(query, [topic_id])
        rows = cursor.fetchall()
        cats = []
        for row in rows:
            cats.append(row[0])

    return cats

def valid_topic_id(id):
    topics = get_topics()
    valid = False

    if isanint(id):
        theid = int(id)
    else:
        return False

    for topic in topics:
        if topic['id'] == theid:
            valid = True
            break

    return valid

def get_lexicon_categories():
    query = 'SELECT word, category FROM interview.management_lexicon'

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    categories = defaultdict(lambda: [])
    for row in rows:
        categories[row[1]].append(row[0])

    return categories

def add_lexicon_words(lexicon_name, words_list):
    add_words_sql = 'INSERT IGNORE INTO interview.management_lexicon (word, category) VALUES (%s, %s)'

    with connection.cursor() as cursor:
        insert_values = [(word, lexicon_name) for word in words_list]
        cursor.executemany(add_words_sql, insert_values)
        transaction.commit()

def delete_lexicon_word(lexicon_name, lexicon_word):
    delete_word_sql = 'DELETE FROM interview.management_lexicon WHERE word=%s AND category=%s'

    with connection.cursor() as cursor:
        cursor.execute(delete_word_sql, [lexicon_word, lexicon_name])
        transaction.commit()

def get_word_count_chart_data(topic):
    query = "SELECT word_count FROM interview.summary WHERE topic=%s"

    with connection.cursor() as cursor:
        cursor.execute(query, [topic])
        rows = cursor.fetchall()

    totals = []
    bins = {i: 0 for i in range(10)}
    bin_labels = [str(i) for i in bins] # no graph will appear anyway
    for row in rows:
        totals.append(row[0])

    if len(totals) > 0:
        tmax = max(totals)
        tbins = [0]
        bin_labels = []
        for i in range(10):
            bin_mark = round(tmax/10 * (i+1))
            tbins.append(bin_mark)
        bins = {t: 0 for t in tbins}
        for j in range(len(tbins)-1):
            bin_labels.append(str(tbins[j]) + '-' + str(tbins[j+1]) + ' words')
        for i in totals:
            for j in range(len(tbins)-1):
                if i > tbins[j] and i <= tbins[j+1]:
                    bins[tbins[j+1]] += 1
                    break

    data_dist = []
    for j in range(len(tbins)-1):
        data_dist.append(bins[tbins[j+1]])
    
    return data_dist, bins, bin_labels

def get_topics_chart_data(topic):
    topics_data = defaultdict(lambda: {'data': []})
    query = """SELECT A.id, B.name, B.count
               FROM interview.summary AS A
               JOIN interview.category AS B ON A.id=B.summary_id
               WHERE topic=%s"""

    with connection.cursor() as cursor:
        cursor.execute(query, [topic])
        rows = cursor.fetchall()

        for row in rows:
            topics_data[row[1]]['name'] = row[1]
            topics_data[row[1]]['data'].append(row[2])

    conv_counts = {k: len(v['data']) for k,v in topics_data.items()}
    topics_data = [v for k,v in topics_data.items()]

    return topics_data, conv_counts

def extract_all_conversations(topic):
    query = """
        SELECT * FROM summary WHERE topic=%s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [topic])
        rows = cursor.fetchall()

    query_session_id = "SELECT * FROM chat WHERE session_id=%s"
    query_user_id = "SELECT * FROM chat WHERE user_id=%s"
    all_chats = []

    counter = 0
    for row in rows:
        if row[2] is not None:
            with connection.cursor() as cursor:
                cursor.execute(query_session_id, [row[2]])
                current_chat = cursor.fetchall()

            all_chats.append(process_chats(current_chat))

        else:
            with connection.cursor() as cursor:
                cursor.execute(query_user_id, [row[1]])
                current_chat = cursor.fetchall()

            all_chats.append(process_chats(current_chat))
        
        counter = counter + 1
    
    csv_file = "write/static/all_conversations_" + topic +  ".csv"
    df = pd.DataFrame(all_chats)
    df.to_csv(csv_file, index=False)

    return "/interview/static/all_conversations_" + topic +".csv"

def process_chats(chats):
    dict_to_return = {}

    chat_keys = ['id', 'question', 'response', 'datetime']
    counter = 0
    for chat in chats:
        counter = counter + 1
        questions_maps = chat[3].split(',')
        question = agent.render_prompt(questions_maps, None)
        current_dict = create_dictionary(chat_keys, [chat[0], question, chat[4], chat[5]])
        dict_to_return[counter] = current_dict

    return dict_to_return

def process_responses(responses):
    responsesToReturn = ""

    for response in responses:
        if responsesToReturn == "":
            responsesToReturn = response[0]
        else:
            responsesToReturn = responsesToReturn + '. ' + response[0]

    return responsesToReturn 

def runLdaModel(topic, numTopics):
    query = """
        SELECT * FROM summary WHERE topic=%s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, [topic])
        rows = cursor.fetchall()

    query_session_id = "SELECT response FROM chat WHERE session_id=%s"
    query_user_id = "SELECT response FROM chat WHERE user_id=%s"
    corpus = []

    for row in rows:
        if row[2] is not None:
            with connection.cursor() as cursor:
                cursor.execute(query_session_id, [row[2]])
                current_chat = cursor.fetchall()

            corpus.append(process_responses(current_chat))

        else:
            with connection.cursor() as cursor:
                cursor.execute(query_user_id, [row[1]])
                current_chat = cursor.fetchall()

            corpus.append(process_responses(current_chat))

    file_path = os.path.dirname(os.path.dirname(__file__)) + "/management/scripts/lda.py"

    now = datetime.now()
    
    file_name = str(now).replace(' ', '_')
    file_name = str(file_name).replace(':', '_')
    file_name = str(file_name).replace('.', '_') + ".json"
    file_name = os.path.dirname(os.path.dirname(__file__)) + "/management/scripts/lda_corpus/" + file_name
    
    with open(file_name, 'w+') as f:
        json.dump(corpus, f)

    # process = subprocess.Popen(['python', file_path, file_name, str(numTopics), topic], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)
    cmd = 'python ' + file_path + ' ' + file_name + ' ' + str(numTopics) + ' ' + str(topic)
    # cmd = ' '.join(['python', file_path, file_name, numTopics, topic])
    # print(cmd)
    # process = subprocess.Popen(['python', file_path, file_name, str(numTopics), topic])
    process = subprocess.Popen(cmd.split(' '))
    # result = subprocess.run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    # return process.communicate()
    # process.wait()

def getLastTenLDA(topic):
    query = 'select * from management_lda where topic = %s order by startingDate desc' #limit 10
    with connection.cursor() as cursor:
        cursor.execute(query, [topic])
        desc = cursor.description

        return [
            dict(zip([col[0] for col in desc], row)) 
            for row in cursor.fetchall() 
        ]
        
def checkLdaStatus():
    query = 'select id, topic from management_lda where status = %s'
    with connection.cursor() as cursor:
        cursor.execute(query, ['running'])
        rows = cursor.fetchall() 

    if len(rows) > 0:
        return False
    else:
        return True

def extractLdaResults(ldaId):
    query = 'select * from management_lda where id = %s'
    with connection.cursor() as cursor:
        cursor.execute(query,[ldaId])
        rows = cursor.fetchall() 

    outputFile = rows[0][6]
    topic = rows[0][7]
    pyLDAvisOutputFile = rows[0][11]
    
    with open(outputFile, 'rb') as f:
        results = pickle.load(f)

    if pyLDAvisOutputFile != None:
        with open(pyLDAvisOutputFile, 'rb') as f:
            pyLDAvisHTML = f.read().decode('utf-8')
    else:
        pyLDAvisHTML = None

    
    terms = {}
    labels = []
    distribution = []

    for key, value in results.items():
        labels.append('Topic' + str(key + 1))
        terms[key + 1] = {}
        terms[key + 1]['terms'] = value['terms']
        distribution.append(value['probability'])
        # print(value.items())
        if 'topic_name' in value and value['topic_name'] is not None:
            terms[key+1]['topicName'] = value['topic_name']
        else:
            terms[key+1]['topicName'] = ''
    return topic, labels, terms, distribution, pyLDAvisHTML

def runBertopic(topic, numTopics):
    query = """
        SELECT * FROM summary WHERE topic=%s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [topic])
        rows = cursor.fetchall()

    query_session_id = "SELECT response FROM chat WHERE session_id=%s"
    query_user_id = "SELECT response FROM chat WHERE user_id=%s"
    corpus = []

    # print('number of rows: ' + str(len(rows)))
    for row in rows:
        if row[2] is not None:
            with connection.cursor() as cursor:
                cursor.execute(query_session_id, [row[2]])
                current_chat = cursor.fetchall()

            corpus.append(process_responses(current_chat))

        else:
            with connection.cursor() as cursor:
                cursor.execute(query_user_id, [row[1]])
                current_chat = cursor.fetchall()

            corpus.append(process_responses(current_chat))

    file_path = os.path.dirname(os.path.dirname(__file__)) + "/management/scripts/bertopic_script.py"

    now = datetime.now()
    
    file_name = str(now).replace(' ', '_')
    file_name = str(file_name).replace(':', '_')
    file_name = str(file_name).replace('.', '_') + ".json"
    file_name = os.path.dirname(os.path.dirname(__file__)) + "/management/scripts/lda_corpus/" + file_name
    
    with open(file_name, 'w+') as f:
        json.dump(corpus, f)

    # process = subprocess.Popen(['python', file_path, file_name, str(numTopics), topic], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)
    cmd = 'python ' + file_path + ' ' + file_name + ' ' + str(numTopics) + ' ' + str(topic)
    # pparams = [sys.executable, file_path, file_name, str(numTopics), topic]
    # process = subprocess.Popen(pparams)
    process = subprocess.Popen(cmd.split(' '))
    # return process.communicate()
    # process.wait()

def getLastTenBertopic(topic):
    query = 'select * from management_bertopic where topic = %s order by startingDate desc' #limit 10
    with connection.cursor() as cursor:
        cursor.execute(query, [topic])
        desc = cursor.description

        return [
            dict(zip([col[0] for col in desc], row)) 
            for row in cursor.fetchall() 
        ]
        
def checkBertopicStatus():
    query = 'select * from management_bertopic where status = %s'
    with connection.cursor() as cursor:
        cursor.execute(query, ['processing'])
        rows = cursor.fetchall() 

    if len(rows) > 0:
        return False
    else:
        return True

def extractBertopicResults(ldaId):
    query = 'select * from management_bertopic where id = %s'
    with connection.cursor() as cursor:
        cursor.execute(query,[ldaId])
        rows = cursor.fetchall() 

    outputFile = rows[0][7]
    topic = rows[0][9]
    pyLDAvisOutputFile = rows[0][8]

    print(outputFile)
    print("*"*100)
    with open(outputFile, 'rb') as f:
        results = pickle.load(f)

    if pyLDAvisOutputFile != None:
        with open(pyLDAvisOutputFile, 'rb') as f:
            pyLDAvisHTML = f.read().decode('utf-8')
    else:
        pyLDAvisHTML = None

    
    terms = {}
    labels = []
    distribution = []

    for key, value in results.items():
        labels.append('Topic' + str(key + 1))
        terms[key + 1] = {}
        terms[key + 1]['terms'] = value['terms']
        distribution.append(value['probability'])
        if 'topic_name' in value and value['topic_name'] is not None:
            terms[key+1]['topicName'] = value['topic_name']
        else:
            terms[key+1]['topicName'] = 'test'
    return topic, labels, terms, distribution, pyLDAvisHTML

def deleteConversation(sessionId, userId):
    if sessionId is not None:
        queries = [
            """DELETE FROM chat WHERE session_id = %s""",
            """DELETE FROM survey WHERE session_id = %s""",
            """DELETE FROM feedback WHERE session_id = %s""",
            """DELETE FROM summary WHERE session_id = %s""",
        ]

        for query in queries:
            with connection.cursor() as cursor:
                cursor.execute(query, [sessionId])
                transaction.commit()

    elif userId is not None:
        queries = [
            """DELETE FROM chat WHERE user_id = %s""",
            """DELETE FROM survey WHERE user_id = %s""",
            """DELETE FROM feedback WHERE user_id = %s""",
            """DELETE FROM summary WHERE user_id = %s""",
        ]

        for query in queries:
            with connection.cursor() as cursor:
                cursor.execute(query, [userId])
                transaction.commit()
    
def extractInteractions(token, topic):
    interactions = {}
    query = """SELECT * FROM chat WHERE (response LIKE %s) AND topic = %s"""
    with connection.cursor() as cursor:
        cursor.execute(query, ['%' + token + '%', topic])
        rows = cursor.fetchall()

    for row in rows:
        interactions[row[2]] = {'text': row[4], 'int_id': row[0]}

    return interactions

def getAllFAQ(topic):
    query = """SELECT * FROM management_faq WHERE topic = %s"""
    with connection.cursor() as cursor:
        cursor.execute(query, [topic])

        return dictfetchall(cursor)

def addFAQ(topic, question, answer):
    add_code_sql = 'INSERT INTO management_faq (topic, question, answer) VALUES (%s,%s,%s)'
    with connection.cursor() as cursor:
        cursor.execute(add_code_sql, (topic, question, answer))
        transaction.commit()

def editFAQ(id, question, answer):
    query = """UPDATE management_faq 
    SET question = %s,
    answer = %s
    WHERE id = %s"""

    with connection.cursor() as cursor:
        cursor.execute(query, [question, answer, id])
        transaction.commit()

def deleteFAQ(id):
    query = """DELETE FROM management_faq WHERE id = %s"""

    with connection.cursor() as cursor:
        cursor.execute(query, [id])
        transaction.commit()

def getAllInterviews(topic):
    query = """SELECT * FROM management_interview WHERE topic_id = %s"""

    with connection.cursor() as cursor:
        cursor.execute(query, [topic])

        return dictfetchall(cursor)

def get_interview_with_questions(id):
    queryInterview = """SELECT * FROM management_interview WHERE id = %s"""
    with connection.cursor() as cursor:
        cursor.execute(queryInterview, [id])
        interview = dictfetchall(cursor)

    queryQuestion = """SELECT * FROM management_question WHERE interview_id = %s"""
    with connection.cursor() as cursor:
        cursor.execute(queryQuestion, [id])
        questions = dictfetchall(cursor)

    queryReflection = """SELECT * FROM management_reflection WHERE interview_id = %s"""
    with connection.cursor() as cursor:
        cursor.execute(queryReflection, [id])
        reflections = dictfetchall(cursor)

    # id_dict = {r['id']: r for r in reflections}

    for reflection in reflections:
        reflection['conditions'] = json.loads(reflection['conditions'])
        reflection['trigger_string'] = []

        if reflection['conditions']['dom_top'] != '':
            reflection['trigger_string'].append('category=' + reflection['conditions']['dom_top'])
        if reflection['conditions']['sentiment'] != '':
            reflection['trigger_string'].append('sentiment=' + reflection['conditions']['sentiment'])
        if reflection['conditions']['reflected'] != '':
            rid = reflection['conditions']['reflected']
            reflection['trigger_string'].append('reflected=' + rid[rid.index('_')+1:])
        if reflection['conditions']['not_reflected'] != '':
            rid = reflection['conditions']['not_reflected']
            reflection['trigger_string'].append('not_reflected=' + rid[rid.index('_')+1:])
        
        reflection['trigger_string'] = ' AND '.join(reflection['trigger_string'])

    return interview, questions, reflections

def activate_interview(id, topic):
    deactivateQuery = 'UPDATE management_interview SET active=%s WHERE active=%s AND topic_id=%s'
    with connection.cursor() as cursor:
        cursor.execute(deactivateQuery, [0, 1, topic])
        transaction.commit()

    activateQuery = 'UPDATE management_interview SET active=%s WHERE id=%s AND topic_id=%s'
    with connection.cursor() as cursor:
        cursor.execute(activateQuery, [1, id, topic])
        transaction.commit()

def create_interview(topic, respect_order, status, note, questions, reflections):
    add_code_sql = 'INSERT INTO management_interview (topic_id, respect_order, active, note, created_at, updated_at) VALUES (%s,%s,%s,%s,%s,%s)'
    with connection.cursor() as cursor:
        cursor.execute(add_code_sql, [topic, respect_order, 0, note, datetime.now(), datetime.now()])
        transaction.commit()
    
    interview_id = cursor.lastrowid
    create_questions(questions, topic, interview_id)
    create_reflections(reflections, interview_id)

    if status:
        activate_interview(interview_id, topic)

def create_questions(questions, topic, interview_id):
    for question in questions:
        query = "INSERT INTO management_question (topic_id, question, interview_id, question_order, conclusion, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        with connection.cursor() as cursor:
            cursor.execute(query, [topic, question['question'], interview_id, int (question['order']), '', datetime.now(), datetime.now()])

            transaction.commit()

def create_reflections(reflections, interview_id):
    reflection_ids = {}
    for i, reflection in enumerate(json.loads(reflections)):
        query = "INSERT INTO management_reflection (reflection, interview_id, conditions, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)"
        with connection.cursor() as cursor:
            cursor.execute(query, [reflection['reflection'].strip(), interview_id, '', datetime.now(), datetime.now()])
            reflection_id = cursor.lastrowid
            reflection_ids[f'reflection_{i+1}'] = reflection_id
            transaction.commit()

    for i, reflection in enumerate(json.loads(reflections)):
        conditions = reflection['conditions']
        if conditions['reflected'] != '':
            conditions['reflected'] = 'reflection_' + str(reflection_ids.get(conditions['reflected'], conditions['reflected']))
        if conditions['not_reflected'] != '':
            conditions['not_reflected'] = 'reflection_' + str(reflection_ids.get(conditions['not_reflected'], conditions['not_reflected']))
        query = "UPDATE management_reflection SET conditions = %s WHERE id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, [json.dumps(conditions), reflection_ids[f'reflection_{i+1}']])
            transaction.commit()

def updateInterview(note, active, respect_order, interview_id, topic):
    query = """
            UPDATE management_interview 
            SET note = %s,
            respect_order = %s
            WHERE id = %s
            """

    with connection.cursor() as cursor:
        cursor.execute(query, [note, respect_order, interview_id])
        transaction.commit()

    if active:
        activate_interview(interview_id, topic)

def deactivate_topic(topic):
    query = "UPDATE interview.management_interview SET active=0 WHERE topic_id=%s"

    with connection.cursor() as cursor:
        cursor.execute(query, [topic])
        transaction.commit()

def get_survey_questions(topic):
    query = "SELECT id, type, text, intro, outro FROM interview.management_survey WHERE topic=%s"

    with connection.cursor() as cursor:
        cursor.execute(query, [topic])
        rows = cursor.fetchall()

    questions = []
    for row in rows:
        questions.append({'id': row[0], 'type': row[1], 'text': row[2], 'intro': row[3], 'outro': row[4]})
    return questions

def delete_survey_question(topic_id, question_id):
    query = "DELETE FROM interview.management_survey WHERE topic=%s AND id=%s"

    with connection.cursor() as cursor:
        cursor.execute(query, [topic_id, question_id])
        transaction.commit()

def add_survey_question(topic_id, question, intro, outro, qtype):
    query = 'INSERT INTO interview.management_survey (type, text, topic, intro, outro) VALUES (%s, %s, %s, %s, %s)'

    with connection.cursor() as cursor:
        cursor.execute(query, [qtype, question, topic_id, intro, outro])
        transaction.commit()

def update_survey_question(topic_id, question_id, checked, inout):
    query = 'UPDATE interview.management_survey SET ' + inout + '=%s WHERE id=%s'

    with connection.cursor() as cursor:
        cursor.execute(query, [checked=='true', question_id])
        transaction.commit()

def generate_pdf_interview(topic):
    """"Extract all interviews and questions"""
    interviews = getAllInterviews(topic)
    questions = []
    for interview in interviews:
        _, _questions, _reflections = get_interview_with_questions(interview['id'])
        questions.append(_questions)
    interviews.reverse()
    questions.reverse()

    """Create PDF"""
    pdf = PDF()
    pdf = PDF(format='A4')
    pdf.add_font('DejaVu', '', 'write/static/fonts/DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 14)
    pdf.add_page()

    """Add Title to PDF"""
    pdf.cell(w=210.0, h=40.0, align='C', txt="Interviews History", border=0)
    pdf.ln(20)
    cursor = 60

    """Add interviews & questions to PDF"""
    for index, interview in enumerate(interviews):
        txt = "#" + str(interview['id']) + ", Published on " + interview['created_at'].strftime('%Y-%m-%d')
        txt_width = pdf.get_string_width(txt)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(w=210.0, h=40.0, align='L', txt=txt, border=0)
        cursor = cursor + 40
        pdf.ln(8)
        # Get current position
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.line(x, y + 15, x + txt_width, y+15)
        pdf.ln(20)

        pdf.set_font('DejaVu', '', 10)
        # For currQuestions in questions[index]:
        for indexQ, question in enumerate(questions[index]):
                pdf.multi_cell(0, 5, str(indexQ + 1) + ". " + question['question'], 0, 1)
                # pdf.cell(w=210.0, h=10.0, ln=1, align='L', txt=str(indexQ) + ". " + question['question'], border=0)
                pdf.ln(5)

    """Save PDF"""
    path = "write/static/interviews.pdf"
    pdf.output(path, 'F')

    return "/interview/static/interviews.pdf"


def validate_words_format(lexicon_words):
    pattern = r'((\"[^\"]+\")|(\'[^\']+\')|(\b[^,]+\b))'
    matches = re.findall(pattern, lexicon_words)
    if isinstance(lexicon_words, list):
        return lexicon_words
    if matches:
        return [match[0].strip('\'"') for match in matches]
    return []

def lexicon_in_use(lexicon_category):
    return False  # Mock check

def isanint(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

def handle_uploaded_file(f, fname):
    with open(STATIC_ROOT + 'uploads/' + fname, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def add_topic(name, botname, introDisclaimer, iconfile=None):
    query = 'INSERT INTO interview.management_topics (topic, cpname, intro_disclaimer) VALUES (%s, %s, %s)'
    with connection.cursor() as cursor:
        cursor.execute(query, [name, botname, introDisclaimer])
        transaction.commit()

    topic_id = cursor.lastrowid
    filename = None
    if iconfile is not None:
        filename = str(topic_id) + '.jpg'
        query = 'UPDATE interview.management_topics SET iconfile=%s WHERE id=%s'
        with connection.cursor() as cursor:
            cursor.execute(query, [filename, topic_id])
            transaction.commit()
    return topic_id, filename

def edit_topic(name, botname, introDisclaimer, filename, id):
    query = 'UPDATE interview.management_topics SET topic=%s, cpname=%s, intro_disclaimer=%s, iconfile=%s WHERE id=%s'
    with connection.cursor() as cursor:
        cursor.execute(query, [name, botname, introDisclaimer, filename, id])
        transaction.commit()
