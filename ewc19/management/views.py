
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from . import services
from write import agent
import operator, json
import pickle as pickle
from django.http import JsonResponse
from pprint import pprint

def login(request):
    if request.user.is_authenticated:
        return redirect('management_summary')
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            topics = services.get_topics()
            request.session['topics'] = topics
            try:
                request.session['active_topic'] = topics[0]['name']
                request.session['active_topic_id'] = topics[0]['id']
            except:
                request.session['active_topic'] = None
                request.session['active_topic_id'] = None
            return redirect('management_summary')
        else:
            context = {'error': 'The login details are incorrect.'}
            return render(request, 'login.html', context)

@login_required
def management_summary(request):
    topic = request.session['active_topic']
    topics = services.get_topics()
    icon_image = None
    topic_id = None
    for _t in topics:
        if _t['name'] == topic:
            icon_image = _t['file']
            topic_id = _t['id']

    number_of_interviews = 0
    number_of_chats = services.get_number_of_chats()
    if topic_id in number_of_chats:
        number_of_interviews = number_of_chats[topic_id]

    topics_dist, conv_counts = services.get_topics_chart_data(topic_id)
    
    top_10_counts = []
    top_10_labels = []
    counter = 0
    for k,v in sorted(conv_counts.items(), key=operator.itemgetter(1), reverse=True):
        top_10_counts.append(v)
        top_10_labels.append(k)
        counter += 1
        if counter == 10:
            break

    survey_dict = services.get_survey_distribution(topic_id)
    # pprint(survey_dict)

    context = { 'topic': topic,
                'survey_summary': survey_dict,
                'number_of_interviews': number_of_interviews,
                'topic_summary_counts': top_10_counts,
                'topic_summary_labels': top_10_labels,
                'average_word_count': services.get_average_word_count(topic_id),
                'average_time': services.get_distribution_of_time(topic_id),
                'all_conversations': services.get_all_conversations(topic_id),
                'topics_distribution': topics_dist,
                'icon_image': icon_image,
                'page_id': 'summary',
    }
    return render(request, 'management_summary.html', context)

@login_required
def deleteConversation(request):
    sessionId = request.POST.get('session_id')
    userId = request.POST.get('user_id')
    topic = request.POST.get('topic')
    
    if not (sessionId == 'None'):
        services.deleteConversation(sessionId = sessionId, userId = None)
    if not (userId == 'None'):
        services.deleteConversation(sessionId = None, userId = userId)
    
    request.GET._mutable = True
    request.GET['topic'] = topic
    return management_summary(request)

@login_required
def time_chart(request):
    topic = request.session['active_topic_id']
    time_last_50_conversations = services.get_time_chart_data(topic)
    return render(request, 'charts/time.html', context={'time_last_50_conversations': time_last_50_conversations})

@login_required
def emotions_chart(request):
    topic = request.session['active_topic']
    emotions_distribution = services.get_emotions_chart_data(topic)
    return render(request, 'charts/emotions.html', context = {'emotions_distribution': emotions_distribution})

@login_required
def word_count_chart(request):
    topic = request.session['active_topic_id']
    totals, bins, bin_labels = services.get_word_count_chart_data(topic)
    return render(request, 'charts/word_count.html', context={'totals': totals, 'bins': bins, 'bin_labels': bin_labels})

@login_required
def extract_conversations(request):
    topic = request.session['active_topic_id']
    path = services.extract_all_conversations(topic)
    return HttpResponse(json.dumps(path, indent=4, sort_keys=True, default=str))
        
@login_required
def runLda(request):
    topic = request.session['active_topic_id']
    numTopics = request.GET.get('numTopics')
    try:
        
        return HttpResponse(services.runLdaModel(topic, numTopics), content_type='application/json')
    except Exception as e:
        return HttpResponse(e, content_type='application/json')
        

@login_required
def lda(request):
    topic = request.session['active_topic_id']
    ldas = services.getLastTenLDA(topic)
    topics = services.get_topics()
    icon_image = None
    for _t in topics:
        if _t['id'] == topic:
            icon_image = _t['file']

    context = {
        'topic': topic, 
        'ldas': ldas,
        'icon_image': icon_image,
    }

    return render(request, 'management_lda.html', context)

@login_required
def ldaResults(request):
    ldaId = request.POST.get('ldaId')
    topic, labels, terms, distribution, pyLDAvis = services.extractLdaResults(ldaId)
    # return HttpResponse(pyLDAvis, content_type='application/json')
    return render(request, 'management_lda_results.html', context={'topic': topic, 'labels': labels, 'terms': terms, 'distribution': distribution, 'pyLDAvis': pyLDAvis})
    
@login_required
def checkBertopicStatus(request):
    noLdaIsRunning = services.checkBertopicStatus()
    return HttpResponse(noLdaIsRunning, content_type='application/json')

@login_required
def runBertopic(request):
    topic = request.session['active_topic_id']
    numTopics = request.GET.get('numTopics')
    try:
        return HttpResponse(services.runBertopic(topic, numTopics), content_type='application/json')
    except Exception as e:
        return HttpResponse(e, content_type='application/json')

@login_required
def bertopic(request):
    topic = request.session['active_topic_id']
    ldas = services.getLastTenBertopic(topic)
    topics = services.get_topics()
    icon_image = None
    for _t in topics:
        if _t['id'] == topic:
            icon_image = _t['file']

    context = {
        'topic': topic, 
        'ldas': ldas,
        'icon_image': icon_image,
    }

    return render(request, 'management_bertopic.html', context)

@login_required
def bertopicResults(request):
    ldaId = request.POST.get('ldaId')
    topic, labels, terms, distribution, pyLDAvis = services.extractBertopicResults(ldaId)
    # print(terms)
    # return HttpResponse(pyLDAvis, content_type='application/json')
    return render(request, 'management_bertopic_results.html', context={'topic': topic, 'labels': labels, 'terms': terms, 'distribution': distribution, 'pyLDAvis': pyLDAvis})
    
@login_required
def checkLdaStatus(request):
    noLdaIsRunning = services.checkLdaStatus()
    return HttpResponse(noLdaIsRunning, content_type='application/json')

@login_required
def extractIntractions(request):
    token = request.POST.get('token')
    topic = request.POST.get('topic')

    interactions = json.dumps(services.extractInteractions(token, topic))
    
    return HttpResponse(interactions, content_type='application/json')

@login_required
def survey_start(request):
    topic_id = request.session['active_topic_id']
    question_types = {i['value']: i['name'] for i in agent.get_question_types()}
    page_questions = services.get_survey_questions(topic_id)

    for pq in page_questions:
        pq['type'] = question_types[pq['type']]

    context = {
        'page_id': 'survey',
        'questions': page_questions,
        'type_options': agent.get_question_types(),
    }
    return render(request, 'management_survey.html', context)

@login_required
def toggle_survey_question(request):
    topic_id = request.session['active_topic_id']
    question_id = request.POST.get('question_id')
    checked = request.POST.get('checked')
    inout = request.POST.get('inout')

    if inout not in ['intro', 'outro'] or checked == None or not services.isanint(question_id):
        return HttpResponse('ERROR', content_type='application/json')

    services.update_survey_question(topic_id, question_id, checked, inout)

    return JsonResponse({'status': 'OK', 'message': 'Question ' + str(question_id) + ' was turned ' + ('on' if checked == 'true' else 'off') + ' for the ' + inout + '.'})

@login_required
def survey_add(request):
    topic_id = request.session['active_topic_id']
    question = request.POST.get('new_question')
    intro = request.POST.get('intro_question')
    outro = request.POST.get('outro_question')
    qtype = request.POST.get('question_type')

    intro = 1 if intro != None else 0
    outro = 1 if outro != None else 0

    qt_list = [i['value'] for i in agent.get_question_types()]
    if qtype not in qt_list or not question or question.strip() == '':
        return redirect('management_survey')

    services.add_survey_question(topic_id, question, intro, outro, qtype)
    return redirect('management_survey')

@login_required
def survey_delete(request):
    topic_id = request.session['active_topic_id']
    question_id = request.POST.get('question_id')

    if not question_id or not services.isanint(question_id):
        return redirect('management_survey')

    services.delete_survey_question(topic_id, question_id)
    return redirect('management_survey')

def indexFAQ(request):
    context = {'page_id': 'faqs', 'no_topic': True}
    if 'active_topic_id' in request.session:
        # print('request session topic id: ' + str(request.session['active_topic_id']))
        faq = services.getAllFAQ(request.session['active_topic_id'])
        context['topic'] = request.session['active_topic_id']
        context['faq'] = faq
        context['no_topic'] = False
    # else:
    #     print('request session topic id: None')
    return render(request, 'management_faq.html', context)

@login_required
def addFAQ(request):
    topic = request.POST.get('topic')
    question = request.POST.get('question')
    answer = request.POST.get('answer')
    services.addFAQ(topic, question, answer)
    return HttpResponse("success", content_type='application/json')


@login_required
def editFAQ(request):
    id = request.GET.get('id')
    question = request.GET.get('question')
    answer = request.GET.get('answer')
    services.editFAQ(id, question, answer)
    
    return HttpResponse("success", content_type='application/json')


@login_required
def deleteFAQ(request):
    id = request.GET.get('id')
    services.deleteFAQ(id)
    
    return HttpResponse("success", content_type='application/json')

@login_required
def interviews(request):
    interviews = services.getAllInterviews(request.session['active_topic_id'])

    return render(request, 'management_interview.html', context={'interviews': interviews, 'page_id': 'interviews'})

@login_required
def interviewDetails(request):
    interviewId = request.GET.get('interviewId')
    interview, questions, reflections = services.get_interview_with_questions(interviewId)
    topic = request.session['active_topic_id']
    topics = services.get_topics()
    icon_image = None
    for _t in topics:
        if _t['id'] == topic:
            icon_image = _t['file']

    return render(request,'management_interview_details.html', context={"interview": interview, "questions": questions, "reflections": reflections,  'icon_image': icon_image})

@login_required
def addNewInterviewGET(request):
    dom_top = services.get_active_lexicons_for_topic(request.session['active_topic_id'])
    sentiment = ['POSITIVE', 'NEGATIVE', 'NEUTRAL']
    topic = request.session['active_topic_id']
    topics = services.get_topics()
    icon_image = None
    for _t in topics:
        if _t['id'] == topic:
            icon_image = _t['file']

    return render(request, 'management_add_new_interview.html', context={'dom_top': dom_top, 'sentiment': sentiment, 'icon_image': icon_image})

@login_required
def addNewInterview(request):
    topic = request.POST.get('topic')
    respectOrder = request.POST.get('respectOrder')
    questions = request.POST.get('questions')
    setAsActive = request.POST.get('setAsActive')
    note = request.POST.get('note')
    reflections = request.POST.get('reflections')

    questions = json.loads(questions)
    oob_count = 0
    qdict = {}
    for question in questions:
        if services.isanint(question['order']):
            question['order'] = int(question['order'])
        else:
            question['order'] = oob_count + len(questions)
            oob_count += 1
        qdict[question['order']] = question
    
    i = 1
    for k,v in sorted(qdict.items()):
        v['order'] = i
        i += 1

    questions = qdict.values()

    services.create_interview(topic, respectOrder, setAsActive, note, questions, reflections)

    return HttpResponse("success", content_type='application/json')

@login_required
def updateInterview(request):
    interviewId = request.POST.get('interviewId')
    setAsActive = request.POST.get('setAsActive')
    respectOrder = request.POST.get('respectOrder')
    note = request.POST.get('note')
    services.updateInterview(note, setAsActive == '1', respectOrder, interviewId, request.session['active_topic_id'])

    return HttpResponse("success", content_type='application/json')

@login_required
def deactivate_interview(request):
    topic_id = request.GET.get('topic')
    if services.isanint(topic_id):
        print('tid: ' + str(topic_id))
        services.deactivate_topic(topic_id)

    return redirect('management_interview')

@login_required
def lexicons_start_page(request, startType=None):
    lexicons_data = dict(services.get_lexicon_categories())

    context = {'lexicons_data': lexicons_data, 'start_type': startType if startType in lexicons_data else None}
    return render(request, 'management_lexicons_startpage.html', context)

@login_required
def lexicon_assignment(request):
    topics = services.get_lexicon_assignments()
    categories = services.get_valid_lexicons()
    context = {'topics': topics, 'categories': categories}
    return render(request, 'management_lexicons_assignment.html', context)

@login_required
def lexicon_assign(request):
    action = request.POST.get('action')
    topic_id = request.POST.get('new_top')
    category = request.POST.get('new_cat')

    if services.isanint(topic_id):
        topic_id = int(topic_id)
        if action == 'add':
            topics = services.get_lexicon_assignments()
            can_add = True
            for _t in topics:
                if _t['id'] == topic_id:
                    if category in _t['categories']:
                        can_add = False
                        break
            if can_add:
                services.add_lexicon_assignment(topic_id, category)
        elif action == 'remove':
            services.remove_lexicon_assignment(topic_id, category)
    
    return redirect('lexicon_assignment')

@login_required
def set_topic(request):
    page_id = request.POST.get('page_id')
    topic_id = request.POST.get('new_active_topic')
    topic_id = int(topic_id) if services.isanint(topic_id) else topic_id
    if page_id and topic_id and page_id != -1:
        for _t in request.session['topics']:
            if _t['id'] == topic_id:
                request.session['active_topic'] = _t['name']
                request.session['active_topic_id'] = _t['id']
        if page_id == 'lexicons':
            return redirect('management_lexicons')
        elif page_id == 'interviews':
            return redirect('management_interview')
        elif page_id == 'faqs':
            return redirect('management_faq_index')
        elif page_id == 'summary':
            return redirect('management_summary')
        elif page_id == 'survey':
            return redirect('management_survey')
    return redirect('management_summary')

@login_required
def topics(request):
    topics = services.get_topics()
    return render(request, 'management_topics.html', context={'topics': topics})

def generate_pdf_interview(request):
    response = services.generate_pdf_interview(request.session['active_topic_id'])
    return HttpResponse(response, content_type='application/json')

@login_required
def add_lexicon(request):
    if request.method == "POST":

        if not request.POST.get('category') or request.POST.get('category').strip() == '':
            return JsonResponse({'status': 'ERROR', 'message': 'The lexicon needs a category.'})
        if not request.POST.get('lexicon_words'):
            return JsonResponse({'status': 'ERROR', 'message': 'There are no words to add.'})

        # Capitalize the name
        lexicon_name = request.POST.get('category').upper()
        # Split by comma to get the words list
        words_list = request.POST.get('lexicon_words').split(',')
        # Clean and format the words
        words_list = [word.strip().strip('"').strip("'") for word in words_list]
        words_list = [word for word in words_list if word != '']

        if len(words_list) == 0:
            return JsonResponse({'status': 'ERROR', 'message': 'There are no words to add.'})

        services.add_lexicon_words(lexicon_name, words_list)

        return JsonResponse({'status': 'OK', 'message': 'Lexicon added successfully! Reload the page to view.'})

    return JsonResponse({'status': 'Invalid request method'})

# TODO: Check if the lexicon is currently in use
@login_required
def delete_lexicon(request):
    lexicon_name = None
    if request.method == "POST":
        # Capitalize the name
        lexicon_name = request.POST.get('deleteType')
        lexicon_word = request.POST.get('deleteWord')

        # TODO: Would be better to have an error and ajax reload
        if lexicon_name and lexicon_word:
            services.delete_lexicon_word(lexicon_name, lexicon_word)

    return lexicons_start_page(request, startType=lexicon_name)

@login_required
def new_topic(request):
    return render(request, 'management_add_topic.html')

@login_required
def add_topic(request):
    if request.method == 'POST':
        try:
            iconFile = request.FILES['files[]']
        except:
            iconFile = None
        topicName = request.POST['topicName']
        botName = request.POST['botName']
        introDisclaimer = request.POST['introDisclaimer']
        subTopicId = None
        if 'topicId' in request.POST:
            subTopicId = int(request.POST['topicId']) if services.isanint(request.POST['topicId']) else None
        subType = request.POST['submitType']

        if subType == 'add':
            # First get the row submitted and get the ID
            topic_id, filename = services.add_topic(topicName, botName, introDisclaimer, iconFile)
        else:
            filename = str(subTopicId) + '.jpg'
            services.edit_topic(topicName, botName, introDisclaimer, filename, subTopicId)
        
        # Then upload the file
        if iconFile:
            print('updating icon ' + filename)
            services.handle_uploaded_file(iconFile, filename)

        if subTopicId != None:
            topic_id = subTopicId

        # Reload topics
        topics = services.get_topics()
        request.session['topics'] = topics
        for topic in topics:
            if topic['id'] == topic_id:
                request.session['active_topic'] = topic['name']
                request.session['active_topic_id'] = topic['id']
                break

        return JsonResponse({'status': 'OK', 'message': 'Topic added successfully! Reload the page to view.'})

    return JsonResponse({'status': 'ERROR', 'message': 'Incorrect post method.'})
