from datetime import datetime
import pickle
import sys
import json
import re
import gensim
from nltk.corpus import stopwords
import spacy
from gensim import corpora
import mysql.connector
from db_settings import *
import nltk
import os
from gensim.models.coherencemodel import CoherenceModel
import statistics
import pyLDAvis.gensim_models as gensimvis
import pyLDAvis
from transformers import pipeline
from nltk.tag import pos_tag

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

if __name__ == '__main__':
    def cleanText(text):
        text = text.lower() #lowercase
        text = text.lstrip() #Removing extra spaces
        # text = text.you() #Removing extra spaces 
        text = re.sub(' +', ' ', text) #Removing extra spaces again 
        text = text.replace('[^A-Za-z0-9]+', ' ') #Removing Numbers, and Special Character 
        text = text.replace("\\", ' ') #Removing backslashes
        text = re.sub(r'[?|$|.|!]',r'',text) #Removing Punctuations,
        text = text.replace('<br/>', ' ')
        return text

    def remove_stopwords_and_pronouns(text):
        # Get the list of stop words for a specific language (e.g., English)
        stop_words = set(stopwords.words('english'))
        
        # Additional general words to be removed
        general_words = ['think', 'know', 'yeah', 'cool', 'mean', 'yes', 'no', 'i', 'like', 'would', 'want', 'something', 'litte', 'explain', 'ask', 'answer', 'question', 'not', 'okay', 'like', 'mmhmm', 'mmhm', 'yep', 'yeah', 'nt', 'also', 'still', "n't", 'nope', 'really', 'sure']
        
        # Merge the stop words and general words
        stop_words.update(general_words)
        
        # Tokenize the text into words
        words = nltk.word_tokenize(text)
        
        # Tag the words with their parts of speech
        tagged_words = pos_tag(words)
        
        # Remove stop words and pronouns
        filtered_words = [word for word, tag in tagged_words if word.lower() not in stop_words and tag != 'PRP']
        
        # Join the filtered words back into a sentence
        filtered_text = ' '.join(filtered_words)
        
        filtered_text = filtered_text.replace('. ', '')
        filtered_text = filtered_text.replace(', ', '')
        filtered_text = filtered_text.replace('?', '')
        filtered_text = filtered_text.replace('!', '')
        
        return filtered_text.strip()

    def sent_to_words(convos):
        for convo in convos:
            convo = cleanText(convo)
            yield(gensim.utils.simple_preprocess(str(convo), deacc=True))  # deacc=True removes punctuations

    # Define functions for stopwords, bigrams, trigrams and lemmatization
    def remove_stopwords(texts):
        return [[word for word in gensim.utils.simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]

    def make_bigrams(texts):
        return [bigram_mod[doc] for doc in texts]

    def make_trigrams(texts):
        return [trigram_mod[bigram_mod[doc]] for doc in texts]

    def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
        """https://spacy.io/api/annotation"""
        texts_out = []
        for sent in texts:
            doc = nlp(" ".join(sent)) 
            texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
        return texts_out
    
    def generate_ldavis_html(lda_model, corpus, dictionary):
        vis_data = gensimvis.prepare(lda_model, corpus, dictionary, mds='tsne')
        pyLDAvis_html = pyLDAvis.prepared_data_to_html(vis_data)
        return pyLDAvis_html

    def updateDB(topic, startingDate, corpusFile, numTopics, status, endingDate, outputFile, id, coherence, error, htmlFile):
        mydb = mysql.connector.connect(
            host=os.environ.get('MYSQL_HOST', '127.0.0.1'),
            user = os.environ.get('MYSQL_USER', 'admin'),
            password = os.environ.get('MYSQL_PASSWORD', 'admin'),
            database = os.environ.get('MYSQL_DATABASE', 'interview'),
            port = os.environ.get('MYSQL_PORT', '3306')
        )
        
        if endingDate is not None and id is not None:
            duration = (endingDate - startingDate).total_seconds()
            query = """UPDATE management_lda
            SET endingDate = %s,
            duration = %s,
            outputFile = %s,
            status = %s,
            coherence = %s,
            error = %s,
            HTMLoutputFile = %s
            WHERE id = %s"""
            with mydb.cursor(buffered=True) as cursor:
                cursor.execute(query, [endingDate, duration, outputFile, status, coherence, error, htmlFile, id])
                mydb.commit()
        else:
            duration = None
            query = 'INSERT INTO management_lda (startingDate, endingDate, duration, corpusFile, outputFile, topic, numTopics, status, coherence, error) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            with mydb.cursor(buffered=True) as cursor:
                cursor.execute(query, [startingDate, endingDate, duration, corpusFile, outputFile, topic, numTopics, status, coherence, error])
                mydb.commit()
                return cursor.lastrowid


            


    with open(sys.argv[1]) as f:
        data = json.load(f)

    NUM_TOPICS = int(sys.argv[2])
    startingDate = datetime.now()

    ID = updateDB(sys.argv[3], startingDate, sys.argv[1], NUM_TOPICS, 'running', None, None, None, None, None, None)

    try:
        nltk.download('stopwords')
        stop_words = stopwords.words('english')
        stop_words.extend(['from', 'subject', 're', 'edu', 'use'])
        
        data_cleaned = []
        for d in data:
            for x in d.split('.'):
                x = remove_stopwords_and_pronouns(x)
                if x != '':
                    data_cleaned.append(x)

        data_words = list(sent_to_words(data_cleaned))
        # Build the bigram and trigram models
        bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100) # higher threshold fewer phrases.
        trigram = gensim.models.Phrases(bigram[data_words], threshold=100)  

        # Faster way to get a sentence clubbed as a trigram/bigram
        bigram_mod = gensim.models.phrases.Phraser(bigram)
        trigram_mod = gensim.models.phrases.Phraser(trigram)

        # Remove Stop Words
        data_words_nostops = remove_stopwords(data_words)

        # Form Bigrams
        data_words_bigrams = make_bigrams(data_words_nostops)

        # Initialize spacy 'en' model, keeping only tagger component (for efficiency)
        nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

        # Do lemmatization keeping only noun, adj, vb, adv
        data_lemmatized = lemmatization(data_words_bigrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])

        # Create Dictionary
        id2word = corpora.Dictionary(data_lemmatized)
        
        # Create Corpus
        texts = data_lemmatized

        # Term Document Frequency
        corpus = [id2word.doc2bow(text) for text in texts]
        # Build LDA model
        lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                                id2word=id2word,
                                                num_topics=NUM_TOPICS, 
                                                random_state=100,
                                                update_every=1,
                                                chunksize=100,
                                                passes=10,
                                                alpha='auto',
                                                per_word_topics=True,
                                                minimum_probability=0.0)

        # Compute Coherence Score
        coherence_model_lda = CoherenceModel(model=lda_model, texts=data_lemmatized, dictionary=id2word, coherence='c_v')
        coherence_lda = coherence_model_lda.get_coherence()
        coherence = float(coherence_lda)
        topics = {}
        for index, topic in lda_model.print_topics():
            terms = str(topic.split(',')).split('+')
            terms_list = []
            for term in terms:
                terms_list.append({str(term.split('*')[1].replace(' ', '').replace('"', '').replace("'", '').replace("]", '')): str(term.split('*')[0].replace("'", '').replace(' ', '').replace('[', '').replace('"', ''))})
            topics[index] = terms_list
        
        probabilities = {}
        for docDist in lda_model.get_document_topics(corpus, minimum_probability=0.0):
            for topicPro in docDist:
                if topicPro[0] not in probabilities:
                    probabilities[topicPro[0]] = [topicPro[1]]
                else:
                    probabilities[topicPro[0]].append(topicPro[1])

        for key in probabilities:
            probabilities[key] = statistics.mean(probabilities[key])
        
        # Genrate topic name
        # classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        # candidate_labels = ['Opinion', 'Organs', 'Diseases', 'Life creation', 'Chimeras', 'Religion', 'Research', 'Commercialization', 'Animals testing', 'cloning', 'Childhood diseases', 'Brain organoids', 'Stem cells', 'Regulation', 'Ethics', 'Transplantation', 'Private companies vs public sector', 'Suffering/Pain', 'Science', 'Ethics in Science', 'Ethics in research', 'Advancements in Science', 'Advancements in research', 'Emotions', 'Science Fiction', 'Artificial Intelligence', 'Policy making']
        
        for key in topics:
            terms_str = ''
            for term in topics[key]:
                terms_str += str(term) + ' '
            

            label = '' #classifier(terms_str, candidate_labels)['labels'][0]
            topics[key] = {'terms': topics[key], 'probability': probabilities[key], 'topic_name': label}

        sorted_values = sorted(topics.values(), key=lambda item: item['probability'], reverse=True)
        topics = {i: value for i, value in enumerate(sorted_values)}

        endingDate = datetime.now()
        basicOutputFile = str(endingDate).replace(' ', '_')
        basicOutputFile = str(basicOutputFile).replace(':', '_')
        basicOutputFile = str(basicOutputFile).replace('.', '_')
        outputFile = os.path.dirname(os.path.dirname(__file__)) + "/scripts/lda_output/" + basicOutputFile + ".pkl"
        HTMLoutputFile = os.path.dirname(os.path.dirname(__file__)) + "/scripts/lda_html_output/" + basicOutputFile + ".txt"

        with open(outputFile, 'wb+') as f:
            pickle.dump(topics, f)

        html = generate_ldavis_html(lda_model, corpus, id2word)
        
        with open(HTMLoutputFile, 'w') as f:
            f.write(html)

        updateDB(sys.argv[3], startingDate, sys.argv[1], NUM_TOPICS, 'done', endingDate, outputFile, ID, coherence, None, HTMLoutputFile)
    except Exception as error:
        endingDate = datetime.now()
        updateDB(sys.argv[3], startingDate, sys.argv[1], NUM_TOPICS, 'failed', endingDate, None, ID, None, str(error), None)
        print(error)