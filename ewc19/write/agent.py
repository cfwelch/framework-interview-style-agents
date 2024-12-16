

import random, json, nltk, pickle, os
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import concurrent.futures

NUM_WORKERS = 4

# This response map object cannot be changed without affecting the SQL database entries.
# The response keys are linked to the 'chat' table 'question' column.
# NOTE: prompts with '_deprecated' in the name will NOT be called by the agent function

# Read the JSON responses file
with open('write/reflections.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Assigning the 'responses' content to RMAP
RMAP = data['responses']

SMESSAGES = {'end_msg': ['Thank you for sharing your thoughts today. Before we provide you with feedback on your writing, can you please answer this brief survey?'],
             'begin_msg': ['Let’s get started. Before we begin, could you please answer the two questions below? When you are ready to start, click \'Next\' to go to the interview questions.']}

SNOTES = {'begin_msg': 'Note: We will not ask for your name, email, or any other private information. Your answers will be stored to help improve the computerized feedback, but they will not be connected to any identifying information.'}

DNOTES = {'question_design': 'Note: This tool is not designed to respond to questions. To receive useful feedback please respond to the given prompts. You can always check our <a target="_blank" href="/interview/admin/management/faq_index/?topic=TOPICTOREPLACE">frequently asked questions</a> section.'}

NUMBER_LT15S = 10
NUMBER_CONNECTOR = 6
NUMBER_REF_GENERIC = 7
LT15SEC_DEPRECATED = [8]
NUMBER_WRITE_ASK = 4

TOO_SHORT_TIME = 15
TOO_SHORT_CHAR = 100
DOMINANCE_THRESHOLD = 0.5

QUESTION_PATTERNS = ["do i", "do you", "is it", "would you","is there",
                    "are there", "is it so", "is this true" , "is that true", "are we", "am i", 
                   "question is", "tell me more", "can i", "can we", "tell me", "can you explain"]

HELPING_VERBS = ["is","am","can", "are", "do", "does"]

QUESTION_TYPES = ["whQuestion","ynQuestion"]

def get_greeting(topic):
    pid = []
    pid.append('interview_intro_v2')
    pid.append('main_q1')
    return pid

def get_question_types():
    qtypes = [
        {'value': 'yesno', 'name': 'Yes/No', 'num_options': 2},
        {'value': 'likert5', 'name': 'Likert 5', 'num_options': 5},
        {'value': 'likert7', 'name': 'Likert 7', 'num_options': 7},
    ]
    return qtypes

def render_convo(convo, session, in_topic):
    if in_topic not in session['logic']:
        in_topic = int(in_topic)
    for turn in convo:
        if turn['agent']:
            turn['text'] = render_prompt(turn['text'], session, in_topic)
            turn['name'] = session['logic'][in_topic]['name']
    return convo

# in_topic is the integer topic
def render_prompt(pid, session, in_topic):
    rp = ''
    # topic = str(in_topic)
    topic = in_topic
    for pp in pid:
        if pp in RMAP:
            trp = RMAP[pp]
        elif pp in session['logic'][topic]['questions']:
            trp = session['logic'][topic]['questions'][pp]['question']
        elif 'main_' in pp:
            question_id = pp.split('_')[1]
            if question_id in session['logic'][topic]['questions']:
                trp = session['logic'][topic]['questions'][question_id]['question']
            else:
                trp = 'This question is no longer in the database.'
        elif pp in session['logic'][topic]['reflections']:
            trp = session['logic'][topic]['reflections'][pp]['reflection']
        elif 'reflection_' in pp:
            reflection_id = pp.split('_')[1]
            # print('reflection id is: ' + str(reflection_id))
            if reflection_id in session['logic'][topic]['reflections']:
                trp = session['logic'][topic]['reflections'][reflection_id]['reflection']
            else:
                trp = 'This reflection is no longer in the database.'
        if '{NAME}' in trp and session is not None:
            trp = trp.replace('{NAME}', session['logic'][topic]['name'])
        if rp != '':
            rp += ' '
        rp += trp
    return rp  

def get_prompt(tokens, categories, qset, ppid, time, in_topic, msg, logic):
    topic = str(in_topic)
    pid = []
    notes = []
    total_len = sum([len(t) for t in tokens])

    # print('logic: ' + str(logic))

    # Use the qset (set of past questions) to determine what to ask next
    options = [i+1 for i in range(logic[topic]['number_main_q']) if 'main_q' + str(i+1) not in qset and logic[topic]['questions']['q' + str(i+1)]['question'] != 'Removed']

    # If they are doing additional writing and are done use these responses
    if len(options) == 0 or 'end_question' in qset:
        if 'end_question' in qset:
            pid.append('end')
        else:
            pid.append('end_question')
    else:
        # If it is the first interaction say their name and provide first prompt
        if 'interview_intro' in ppid:
            pid.append('repeat_name')
            waops = [i+1 for i in range(NUMBER_WRITE_ASK)]
            pid.append('write_ask' + str(random.choice(waops)))
            pid.append('main_q1')

        rnames = {k: v for k,v in logic[topic]['reflections'].items()}
        dom_cat, sentiment = process_text(msg, rnames, categories)
        dom_cat, sentiment = dom_cat.result(), sentiment.result()

        for reflection_name, reflection in logic[topic]['reflections'].items():
            if reflection_applies(reflection, reflection_name, qset, dom_cat, sentiment):
                pid.append(reflection_name)
                break

        # If the response is too short ask them to elaborate and the last thing we said was not one of these.
        if (total_len < TOO_SHORT_CHAR or time < TOO_SHORT_TIME) and not has_too_short(qset) and not has_reflection(ppid):
            ltop = [i+1 for i in range(NUMBER_LT15S) if 'lt15sec' + str(i+1) not in qset and i+1 not in LT15SEC_DEPRECATED]
            if len(ltop) == 0:
                ltop = [i+1 for i in range(NUMBER_LT15S) if i+1 not in LT15SEC_DEPRECATED]
            pid.append('lt15sec' + str(random.choice(ltop)))
        # Otherwise ask the next prompt
        if len(pid) == 0:
            conops = [i+1 for i in range(NUMBER_CONNECTOR)]
            waops = [i+1 for i in range(NUMBER_WRITE_ASK)]
            pid.append('connector' + str(random.choice(conops)))
            if logic[topic]['respect_order']:
                pid.append('main_q' + str(options[0]))
            else:
                pid.append('main_q' + str(random.choice(options)))
            pid.append('write_ask' + str(random.choice(waops)))

    if is_question(msg) != False:
        notes.append(DNOTES['question_design'].replace('TOPICTOREPLACE', topic))

    return pid, notes

def has_reflection(pastids):
    retv = False
    for ppid in pastids:
        if ppid.startswith('ref_'):
            retv = True
            break
    return retv

def has_too_short(pastids):
    retv = False
    for ppid in pastids:
        if ppid.startswith('lt15sec'):
            retv = True
            break
    return retv

def get_dominant(imap, rnames):
    if 'WORK' in imap.keys():
        del(imap['WORK'])
    top1 = 0
    top2 = 0
    topk = None
    for k,v in imap.items():
        # if there is a topic constraint and this key isn't in the topic then skip it
        if k not in rnames:
            continue
        # update dominant values
        if v > top1:
            top2 = top1
            top1 = v
            topk = k
        elif v > top2:
            top2 = v

    retv = None
    if top1 > 0:
        if top2 > 0:
            if (top1 * 1.0 / top2) - 1.0 > DOMINANCE_THRESHOLD:
                retv = topk
        else:
            retv = topk
    return retv

def dialogue_act_features(post):
    features = {}
    for word in nltk.word_tokenize(post):
        features['contains({})'.format(word.lower())] = True
    return features

def is_ques_using_nltk(ques):
    file_path = os.path.dirname(os.path.dirname(__file__)) + "/write/classifiers/question_classifier.pickle"
    f = open(file_path, 'rb')
    classifier = pickle.load(f)
    f.close()
    question_type = classifier.classify(dialogue_act_features(ques)) 
    return question_type in QUESTION_TYPES


# check with custom pipeline if still this is a question mark it as a question
def is_question(question):
    file_path = os.path.dirname(os.path.dirname(__file__)) + "/write/classifiers/question_classifier.pickle"
    f = open(file_path, 'rb')
    classifier = pickle.load(f)
    f.close()

    question = question.lower().strip()
    if not is_ques_using_nltk(question):
        is_ques = False
        # check if any of pattern exist in sentence
        for pattern in QUESTION_PATTERNS:
            is_ques = pattern in question
            if is_ques:
                break

        # there could be multiple sentences so divide the sentence
        sentence_arr = question.split(".")
        for sentence in sentence_arr:
            if len(sentence.strip()):
                # if question ends with ? or start with any helping verb
                # word_tokenize will strip by default
                first_word = nltk.word_tokenize(sentence)[0]
                if sentence.endswith("?") or first_word in HELPING_VERBS:
                    is_ques = True
                    break
        return is_ques 
    else:
        return classifier.classify(dialogue_act_features(question))

def get_sentiment(msg):
    sid = SentimentIntensityAnalyzer()
    score = sid.polarity_scores(msg)['compound']
    if score >= 0.05:
        return 'POSITIVE'
    elif score <= -0.05:
        return 'NEGATIVE'
    
    return 'NEUTRAL'

def process_text(msg, rnames, categories):
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        dom_cat = executor.submit(get_dominant, categories, rnames)
        sentiment = executor.submit(get_sentiment, msg)
    return dom_cat, sentiment

def reflection_applies(reflection, reflection_name, qset, dom_cat, sentiment):
    is_applicable = True
    if (reflection_name in qset):
        return False

    if reflection['conditions'].get('sentiment') and reflection['conditions']['sentiment'] != sentiment:
        return False

    not_reflected_list = reflection['conditions'].get('not_reflected')
    if not_reflected_list:
        not_reflected_list = not_reflected_list.replace('\'', '').split(', ')
        for not_reflected in not_reflected_list:
            if not_reflected in qset:
                return False

    reflected_list = reflection['conditions'].get('reflected')
    if reflected_list:
        reflected_list = reflected_list.replace('\'', '').split(', ')
        for reflected in reflected_list:
            if reflected not in qset:
                return False

    if reflection['conditions'].get('dom_cat') and reflection['conditions']['dom_cat'] != dom_cat:
        return False

    return is_applicable
