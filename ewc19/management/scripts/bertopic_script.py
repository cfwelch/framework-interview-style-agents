import json
import nltk
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from bertopic import BERTopic
import mysql.connector
from transformers import pipeline
from datetime import datetime
import sys
import gensim.corpora as corpora
from gensim.models.coherencemodel import CoherenceModel
from transformers import pipeline
import os
import pickle
import numpy as np
import pyLDAvis
from bertopic.representation import KeyBERTInspired
from bertopic.vectorizers import ClassTfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

if __name__ == '__main__':
    def remove_stopwords_and_pronouns(text):
        # Get the list of stop words for a specific language (e.g., English)
        stop_words = set(stopwords.words('english'))
        
        # Additional general words to be removed
        general_words = ['think', 'know', 'yeah', 'cool', 'mean', 'yes', 'no', 'i', 'like', 'would', 'want', 'something', 'litte', 'explain', 'ask', 'answer', 'question', 'not', 'okay', 'like', 'mmhmm', 'mmhm', 'yep', 'yeah', 'nt', 'also', 'still', "n't", 'nope', 'really', 'sure', 'thank', 'tell', 'have', 've', "'ve", "'s", "'m", 'thanks', 'told', 'br', '<', '>', '/', 'dont', 'see', 'hmm', 'let', 'feel']
        
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
        filtered_text = filtered_text.replace(':', '')
        filtered_text = filtered_text.replace(' br ', '')
        
        return filtered_text.strip()
    
    #TODO: check and update after migrating db
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
            query = """UPDATE management_bertopic
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
            query = 'INSERT INTO management_bertopic (startingDate, endingDate, duration, corpusFile, outputFile, topic, numTopics, status, coherence, error) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            with mydb.cursor(buffered=True) as cursor:
                cursor.execute(query, [startingDate, endingDate, duration, corpusFile, outputFile, topic, numTopics, status, coherence, error])
                mydb.commit()
                return cursor.lastrowid
            
    def processCorpus(corpus):
        newCorpus = []
        for d in corpus:
            for x in d.split('.'):
                x = remove_stopwords_and_pronouns(x)
                if x != '':
                    newCorpus.append(x)
        return newCorpus
    
    def runBertopic(corpus, numTopics = None):
        if numTopics == 'Auto' or numTopics is None:
            topic_model = BERTopic(calculate_probabilities=True, verbose=True)
        else:
            topic_model = BERTopic(nr_topics = numTopics, calculate_probabilities=True, verbose=True)

        topics, probs = topic_model.fit_transform(corpus)
        return topics, probs, topic_model
    
    def getCoherenceScore(topic_model, corpus):
        cleaned_docs = topic_model._preprocess_text(corpus)
        vectorizer = topic_model.vectorizer_model
        analyzer = vectorizer.build_analyzer()
        tokens = [analyzer(doc) for doc in cleaned_docs]
        dictionary = corpora.Dictionary(tokens)
        corpus = [dictionary.doc2bow(token) for token in tokens]
        topics = topic_model.get_topics()
        # topics.pop(-1, None)
        topic_words = [
        [word for word, _ in topic_model.get_topic(topic) if word != ""] for topic in topics]
        topic_words = [[words for words, _ in topic_model.get_topic(topic)] 
                for topic in range(len(set(topics))-1)]

        # Evaluate
        coherence_model = CoherenceModel(topics=topic_words, 
                                texts=tokens, 
                                corpus=corpus,
                                dictionary=dictionary, 
                                coherence='c_v')
        return coherence_model.get_coherence()
    
    def generatePyLDAvis(topic_model, topics, probs, corpus, basicOutputFile):
        top_n = len(topics)
        topic_term_dists = topic_model.c_tf_idf_.toarray()
        # new_probs = probs[:, :top_n]
        outlier = np.array(1 - probs.sum(axis=1)).reshape(-1, 1)
        doc_topic_dists = np.hstack((probs, outlier))
        doc_lengths = [len(doc) for doc in corpus]
        vocab = [word for word, index in sorted(topic_model.vectorizer_model.vocabulary_.items(), key=lambda x: x[1])]
        term_document_matrix = topic_model.vectorizer_model.transform(corpus)
        term_frequency = term_document_matrix.sum(axis=0).A1

        data = {'topic_term_dists': topic_term_dists,
            'doc_topic_dists': doc_topic_dists,
            'doc_lengths': doc_lengths,
            'vocab': vocab,
            'term_frequency': term_frequency}

        # Visualize using pyLDAvis
        # vis_data= pyLDAvis.prepare(**data, mds='mmds')
        vis_data= pyLDAvis.prepare(**data, mds='mmds', sort_topics=False)
        pyLDAvis_html = pyLDAvis.prepared_data_to_html(vis_data)

        HTMLoutputFile = os.path.dirname(os.path.dirname(__file__)) + "/scripts/lda_html_output/" + basicOutputFile + ".txt"
        with open(HTMLoutputFile, 'w') as f:
            f.write(pyLDAvis_html)
        
        return HTMLoutputFile

    # def generateTopicsLabels(classifier, sequence):
        # candidate_labels = ['Opinion', 'Organs', 'Diseases', 'Life creation', 'Chimeras', 'Religion', 'Research', 'Commercialization', 'Animals testing', 'cloning', 'Childhood diseases', 'Brain organoids', 'Stem cells', 'Regulation', 'Ethics', 'Transplantation', 'Private companies vs public sector', 'Suffering/Pain', 'Science', 'Ethics in Science', 'Ethics in research', 'Advancements in Science', 'Advancements in research', 'Emotions', 'Science Fiction', 'Artificial Intelligence', 'Policy making']
        # return classifier(sequence, candidate_labels)['labels'][0]
        
    def saveOutputFile(topic_model):
        classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        freq = topic_model.get_topic_freq()
        # freq = freq[freq['Topic'] != -1]
        sumDist = freq['Count'].sum()
        toSave = {}
        topics = topic_model.get_topics()
        # topics.pop(-1, None)
        for key in topics:
            terms_str = ''
            terms = []
            for term in topics[key]:

                try:
                    terms.append([term[0], float(term[1])])
                except:
                    terms.append([term[1], float(term[0])])

                terms_str += str(term[0]) + ' '
            topicName = ''#generateTopicsLabels(classifier, terms_str)
            probability = freq.loc[freq['Topic'] == key, 'Count'].values[0] / sumDist
            toSave[key] = {'terms': terms, 'probability': probability, 'topic_name': topicName}
        sorted_values = sorted(toSave.values(), key=lambda item: item['probability'], reverse=True)
        toSave = {i: value for i, value in enumerate(sorted_values)}
        endingDate = datetime.now()
        basicOutputFile = str(endingDate).replace(' ', '_')
        basicOutputFile = str(basicOutputFile).replace(':', '_')
        basicOutputFile = str(basicOutputFile).replace('.', '_') 
        outputFile = os.path.dirname(os.path.dirname(__file__)) + "/scripts/lda_output/" + basicOutputFile + ".pkl"
        
        with open(outputFile, 'wb+') as f:
            pickle.dump(toSave, f)
        
        return basicOutputFile, outputFile

    NUM_TOPICS = sys.argv[2]
    if NUM_TOPICS != 'Auto':
        NUM_TOPICS = int(NUM_TOPICS)
        numTopicsToSave = NUM_TOPICS
    else:
        numTopicsToSave = -1

    startingDate = datetime.now()
    ID = updateDB(sys.argv[3], startingDate, sys.argv[1], numTopicsToSave, 'processing', None, None, None, None, None, None)
    try:
        with open(sys.argv[1], 'r') as f:
            corpus = json.load(f)
        corpus = processCorpus(corpus)
        topics, probs, topic_model = runBertopic(corpus, NUM_TOPICS)
        basicOutputFile, outputFile = saveOutputFile(topic_model)
        HtmlOutputFile = generatePyLDAvis(topic_model, topics, probs, corpus, basicOutputFile)
        endingDate = datetime.now()
        updateDB(sys.argv[3], startingDate, sys.argv[1], numTopicsToSave, 'completed', endingDate, outputFile, ID, getCoherenceScore(topic_model, corpus), None, HtmlOutputFile)
    except Exception as error:
        endingDate = datetime.now()
        updateDB(sys.argv[3], startingDate, sys.argv[1], numTopicsToSave, 'failed', endingDate, None, ID, None, str(error), None)
        print(error)
    

