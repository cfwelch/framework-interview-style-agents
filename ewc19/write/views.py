

import operator, urllib, json, re

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader, RequestContext
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Needed for password updating -- possible future addition
# from django.contrib.auth import update_session_auth_hash
# from django.contrib.auth.forms import PasswordChangeForm

from collections import defaultdict
from . import services, agent
from management import services as mservices

NUMBER_PPL_NORMALIZE = 200
COLOR_CYCLE = ['rgba(84, 71, 140, 1)', 'rgba(44, 105, 154, 1)', 'rgba(4, 139, 168, 1)', 'rgba(13, 179, 158, 1)', 'rgba(22, 219, 147, 1)', 'rgba(131, 227, 119, 1)', 'rgba(185, 231, 105, 1)', 'rgba(239, 234, 90, 1)', 'rgba(241, 196, 83, 1)', 'rgba(242, 158, 76, 1)']

def index(request):
    return redirect('write')

def intro(request):
    if not request.user.is_authenticated:
        context = {}
        topic = None
        if request.method == 'POST':
            if 'topic' in request.POST:
                if mservices.valid_topic_id(request.POST['topic']):
                    topic = int(request.POST['topic'])
            else:
                return render(request, 'logout_first.html', context = {})

        if not request.session.session_key:
            request.session.create()

        # Set the interview logic in the session
        services.set_active_interview(topic, request.session)

        # Prepare the intro survey questions
        questions = services.get_survey_questions(topic, True)
        smsg = agent.SMESSAGES['begin_msg']
        snote = agent.SNOTES['begin_msg']
        context = {'questions': questions, 'before_write': 'true', 'smsg': smsg, 'snote': snote, 'topic': topic}
        return render(request, 'survey.html', context)
    else:
        return render(request, 'logout_first.html', context = {})

def feedback(request):
    context = {}
    if request.method == 'POST':
        clarity = request.POST['clarity']
        summary = request.POST['summary']
        features = request.POST['features']
        other = request.POST['other']

        if clarity.strip() != '' or summary.strip() != '' or features.strip() != '' or other.strip() != '':
            services.submit_feedback(request.session.session_key, clarity, summary, features, other)
        return redirect('summary')
    else:
        return render(request, 'feedback.html', context)

# @login_required
def write(request):
    # First get the topic if it is set
    topic = None
    into = ''

    # Move Prolific variables to the session
    if 'STUDY_ID' in request.GET:
        request.session['STUDY_ID'] = request.GET['STUDY_ID']
    elif 'study_id' in request.GET:
        request.session['STUDY_ID'] = request.GET['study_id']
    if 'SESSION_ID' in request.GET:
        request.session['SESSION_ID'] = request.GET['SESSION_ID']
    elif 'session_id' in request.GET:
        request.session['SESSION_ID'] = request.GET['session_id']
    if 'PROLIFIC_PID' in request.GET:
        request.session['PROLIFIC_PID'] = request.GET['PROLIFIC_PID']
    elif 'prolific_pid' in request.GET:
        request.session['PROLIFIC_PID'] = request.GET['prolific_pid']
    if 'into' in request.GET:
        into = request.GET['into']

    if 'topic' in request.session:
        if mservices.valid_topic_id(request.session['topic']):
            topic = int(request.session['topic'])

    into = int(into) if services.isanint(into) else into
    context = {'topic': topic, 'into': into}
    bws = False
    if topic != None:
        request.session['active_topic_id'] = topic
        bws, aws, _ = services.get_survey_status(request.session.session_key)

    if not bws:
        context['topics'] = mservices.get_topics(active_only=True)
        return render(request, 'intro.html', context)

    # If before survey has been done then get stats to see if conversation has ended
    categories, convo, qset, last_ppid, all_times, total_words, last_timestamp, interview_id = services.get_stats(request.session, topic, request.session.session_key)
    convo = agent.render_convo(convo, request.session, str(topic))
    if len(qset) == 0:
        pid = agent.get_greeting(topic)
    else:
        tokens, categories = services.get_values(convo[-1]['text'], request.session['active_topic_id'])
        for index, question in enumerate(qset):
            if 'main_' in question: ######## TODO WHY DO WE NEED THIS
                for key, value in request.session['logic'][str(topic)]['questions'].items():
                    if value['id'] == question.split('_')[1]:
                        print(' changing qset ' + str(qset[index]) + ' to ' + str(key))
                        qset[index] = key

        pid, notes = agent.get_prompt(tokens, categories, qset, last_ppid.split(','), all_times[-1], topic, convo[-1]['text'], request.session['logic'])
        context['notes'] = notes

    # print(qset)
    if ('end' in qset or 'end' in pid) and not aws:
        questions = services.get_survey_questions(topic, False)
        context['questions'] = questions
        context['before_write'] = 'false'
        context['smsg'] = agent.SMESSAGES['end_msg']
        context['snote'] = None
        return render(request, 'survey.html', context)
    else:
        context['prompt'] = agent.render_prompt(pid, request.session, str(topic))
        context['pid'] = ','.join(pid)
        context['timer'] = True
        context['convo'] = convo
        context['is_complete'] = 'end' in qset or 'end' in pid
        context['agent_name'] = request.session['logic'][str(topic)]['name']
        return render(request, 'write.html', context)

def survey(request):
    if request.method == 'POST':
        bf = 1 if request.POST['before_write'] == 'true' else 0
        answers = defaultdict(lambda: -1)

        topic = None
        if mservices.valid_topic_id(request.POST['topic']):
            topic = int(request.POST['topic'])
            request.session['topic'] = topic
        elif 'topic' in request.session and mservices.valid_topic_id(request.session['topic']):
            topic = int(request.session['topic'])

        for key in request.POST:
            if key.startswith('q_'):
                answers[key[2:]] = int(request.POST[key]) if services.isanint(request.POST[key]) else -1
        services.submit_survey(answers, bf, request.session.session_key, topic)

        # This means it is the post-interview survey, so we go to the summary instead of the interview/writing page
        if bf == 0:
            return redirect('summary')
    return redirect('write')

# This method is mostly for testing purposes
# @login_required
# def delall(request):
#     services.delete_all_chat(request.user.id)
#     context = {'complete': False}
#     return render(request, 'summary.html', context)

# @login_required
def send(request):
    context = {}
    # msg that the user inputs in response to a prompt
    msg = request.POST['message'].strip()
    # get the topic of the conversation
    topic = request.POST['topic'].strip()
    # ID of prompt this msg was a response to
    ppid = request.POST['pid'].split(',')
    # Time the response took
    time = request.POST['time']
    time = int(time) if services.isanint(time) else 0
    tokens, categories = services.get_values(msg, request.session['active_topic_id'])

    # Insert the new prompt-response pair with word counts
    services.add_response(ppid, msg, categories, request.user.id if request.user.is_authenticated else request.session.session_key, time, len(tokens), topic, request.session['interview_id'])

    # If this is the end of the interview, save aggregates from conversation to the summary table
    if 'end_question' in ppid:
        # Get conversation stats
        categories, _, qset, last_ppid, all_times, total_words, _, interview_id = services.get_stats(request.session, topic, request.session.session_key)
        # Submit conversation stats as summary
        services.add_summary(request.session.session_key, categories, sum(all_times), total_words, topic)
    else:
        # Get the set of questions that has been asked before
        qset = services.get_questions(request.session.session_key, topic, request.session['logic'])

    # Get a new prompt using history
    pid, notes = agent.get_prompt(tokens, categories, qset, ppid, time, topic, msg, request.session['logic'])

    # Construct the JSON object to return to AJAX
    context['response'] = agent.render_prompt(pid, request.session, topic)
    context['pid'] = ','.join(pid)
    context['end'] = 'end' in pid
    context['notes'] = notes
    # context['data'] = [] # for charts
    json_data = json.dumps(context)
    return HttpResponse(json_data, content_type='application/json')

def reset(request):
    if request.user.is_authenticated:
        if 'topic' in request.session:
            del request.session['topic']
    else:
        if request.session.session_key:
            request.session.flush()
    return redirect('write')

def list_summary(request):
    if request.user.is_authenticated:
        inters = services.get_interactions(request.user.id)
        if len(inters) > 0:
            context = {'complete': False, 'norm_stats': None, 'agent_name': request.session['logic'][topic]['name'], 'interactions': inters}
            return render(request, 'summary.html', context)

    # if no interactions or user is not logged in
    return redirect('summary')

def summary(request):
    session_id = request.POST.get('session_id', False) if request.user.is_authenticated else request.session.session_key

    if 'active_topic_id' not in request.session:
        return redirect('write')

    topic = request.session['active_topic_id']
    bws, aws, sq = services.get_survey_status(session_id)
    categories, convo, qset, last_ppid, all_times, total_words, last_timestamp, interview_id = services.get_stats(request.session, topic, session_id)

    # If it is yes/no then make it text, else it is likert and not 0-indexed so add 1
    for i in sq:
        if i['type'] == 'yesno':
            if i['answer'] == 0:
                i['answer'] = 'No'
            else:
                i['answer'] = 'Yes'
        else:
            i['answer'] += 1

    survey_questions = {
        'before': [r for r in sq if r['before_writing'] == 1],
        'after': [r for r in sq if r['before_writing'] == 0],
    }

    services.set_active_interview(topic, request.session, interview_id=interview_id)

    convo = agent.render_convo(convo, request.session, str(topic))
    for dict in convo:
        dict['text'] = br_to_newlines(dict['text'])


    # Filter topics not relevant to conversation type
    main_topics = mservices.get_active_lexicons_for_topic(topic)
    topics = {k: v for k,v in categories.items() if k in main_topics}

    tnames = []
    tvals = []
    for k,v in sorted(topics.items(), key=operator.itemgetter(1), reverse=True):
        tvals.append(v)
        tnames.append(k)

    if bws:
        options = [v['id'] for k,v in request.session['logic'][topic]['questions'].items() if v['id'] not in qset]
        # Changed complete to be true if any questions are answered
        is_complete = len(options) == 0
    else:
        is_complete = False
    
    if aws:
        is_complete = True

    if is_complete and not aws and not request.user.is_authenticated:
        questions = services.get_survey_questions(topic, False)
        context = {'questions': questions, 'before_write': 'false', 'smsg': agent.SMESSAGES['end_msg'], 'snote': None}
        return render(request, 'survey.html', context)

    norm_stats = {}
    if is_complete:
        # Create AMT ID
        if 'amt_code' not in request.session:
            # amt_code = services.make_unique_id('amt', request.session.session_key)
            amt_code = services.make_prolific_entry(request.session, session_id, topic)
            request.session['amt_code'] = amt_code

        my_top_norms = {
            tp: topics[tp] * 100.0 / total_words if total_words > 0 else 0 for tp in topics
        }

        # print('last_timestamp: ' + str(last_timestamp))
        remos, rtopics, rpronouns, rttime, rtwords, numents = services.get_recent_user_summaries(last_timestamp, NUMBER_PPL_NORMALIZE, topic)
        # qOrganoids, qOrganoids_favor, qOrganoids_favor_after = services.get_recent_user_surveys(last_timestamp, NUMBER_PPL_NORMALIZE, topic)

        # print('Number of recent entries: ' + str(numents))

        norm_topics = defaultdict(lambda: [])
        net_emos = []
        i_words = []
        # precompute lists
        for i in range(numents):
            net_emos.append(remos['POSEMO'][i] - remos['NEGEMO'][i])
            i_words.append(rpronouns['I'][i] * 1.0 / rtwords[i])
            # for ii in main_topics:
            #     norm_topics[ii].append(rtopics[ii][i] * 1.0 / rtwords[i])
                # norm_topics['POLITICAL'].append(rtopics['POLITICAL'][i] * 1.0 / rtwords[i])

        norm_topics = {k: sum(v) * 100.0 / len(v) for k,v in norm_topics.items()}

        # compute extremes
        ne_min = min(net_emos) if len(net_emos) > 0 and min(net_emos) != 0 else 1
        ne_max = max(net_emos) if len(net_emos) > 0 and max(net_emos) != 0 else 1
        iw_min = min(i_words) if len(i_words) > 0 and min(i_words) != 0 else 1
        iw_max = max(i_words) if len(i_words) > 0 and max(i_words) != 0 else 1

        # renorm lists in 0-10
        for i in range(numents):
            ndenom = ne_max - ne_min if ne_max - ne_min > 0 else 1
            idenom = iw_max - iw_min if iw_max - iw_min > 0 else 1
            net_emos[i] = (net_emos[i] - ne_min) * 10.0 / ndenom
            i_words[i] = (i_words[i] - iw_min) * 10.0 / idenom

        sort_my_top = sorted(my_top_norms.items(), key=operator.itemgetter(1), reverse=True)
        sort_avg_top = sorted(norm_topics.items(), key=operator.itemgetter(1), reverse=True)

        numents = numents if numents > 0 else 1
        norm_stats = {
            'most_discussed': {'you': {'topic': sort_my_top[0][0] if len(sort_my_top) > 0 else 'None',
                                       'percent': '{:.2f}'.format(sort_my_top[0][1]) if len(sort_my_top) > 0 else 0,
                                       'avg_percent': '{:.2f}'.format(norm_topics[sort_avg_top[0][0]]) if len(sort_avg_top) > 0 else 0},
                               'avg': {'topic': sort_avg_top[0][0] if len(sort_avg_top) > 0 else 'None',
                                       'percent': '{:.2f}'.format(sort_avg_top[0][1]) if len(sort_avg_top) > 0 else 0}},
            'least_discussed': {'you': {'topic': sort_my_top[-1][0] if len(sort_my_top) > 0 else 'None',
                                        'percent': '{:.2f}'.format(sort_my_top[-1][1]) if len(sort_my_top) > 0 else 0,
                                        'avg_percent': '{:.2f}'.format(norm_topics[sort_avg_top[-1][0]]) if len(sort_avg_top) > 0 else 0},
                                'avg': {'topic': sort_avg_top[-1][0] if len(sort_avg_top) > 0 else 'None',
                                        'percent': '{:.2f}'.format(sort_avg_top[-1][1]) if len(sort_avg_top) > 0 else 0}},
            'number_words': {'you': total_words, 
                             'avg': int(sum(rtwords) * 1.0 / numents),
                             'avg_2': int(sum(rtwords) * 1.0 / numents / 2),
                             'avg_6': int(sum(rtwords) * 1.0 / numents) / 6},
            'number_minutes': {'you': '{:.1f}'.format(sum(all_times) / 60.0), 'avg': '{:.1f}'.format(rttime / 60.0 / numents)},
        }

        color_map = []
        for i in range(len(tnames)):
            color_map.append(COLOR_CYCLE[i % len(COLOR_CYCLE)])

        context = {'topics': topics, 'convo': convo, 'complete': is_complete, 'norm_stats': norm_stats, 'agent_name': request.session['logic'][topic]['name'], 'tvals': tvals, 'tnames': tnames, 'survey': survey_questions, 'color_map': color_map}
        # return HttpResponse(json.dumps(context))
        return render(request, 'summary.html', context)
    else:
        return redirect('write')

def resources(request):
    return render(request, 'resources.html')

def submit_logout(request):
    logout(request)
    sess_keys = ['name', 'topic']
    for sk in sess_keys:
        if sk in request.session:
            del request.session[sk]
    return redirect('/interview/write')


def custom_404(request, exception):
    return render(request, '404.html', status=404)

def br_to_newlines(text):
    return text.replace('<br/>', '\n')
