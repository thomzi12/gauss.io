import pandas as pd
import numpy as np
import re
import gensim
from emailer import sendEmail
from test2df import pdf2DF
from scipy.spatial.distance import cdist
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()
stopwords = set(stopwords.words("english"))
try:
    import cPickle as pickle
except:
    import pickle


def read_questions(filename):
    '''
    INPUT: filename of pdf of exam submitted by teacher
    OUTPUT: Pandas dataframe with column for question ID, question text
    '''
    return pd.read_csv(filename)

def load_KA_content(filenames):
    '''
    OUTPUT: Pandas dataframe created by topic_builder.py script
    '''
    # try:
    #     df = pd.read_csv(filenames[0])
    # except FileNotFoundError:
    #     df = pickle.load(open(filenames[1], "rb"))
    # return df
    return pickle.load(open(filenames[1], "rb"))

def text_to_bag(q_string, stem = False):
    '''
    INPUT: string of question text
    OUTPUT: stemmed and cleaned text ()
    Note: This approach wouldn't work for a doc2vec approach. That said, math,
    the focus of this prototype, doesn't rely heavily on English semantics
    '''
    q_string = re.sub("[^a-zA-Z]", " ", q_string) # remove numbers and letters.
    # More generally, teachers need to enter in (English) text on what the question is about
    q_list = q_string.lower().split() #lower case all words, split into list of words
    q_list = [word for word in q_list if not word in stopwords] # Don't include words in stopwords
    if stem: # word2vec will map out relationships between words, so not sure this is necessary
        q_list = [stemmer.stem(word) for word in q_list]
    return " ".join(q_list)


def document_to_bags_and_vector(df, text_column, model):
    '''
    INPUT: Pandas dataframe, string of column with text to clean
    OUTPUT: Pandas dataframe but with question text stemmed with `text_to_bag()`
    '''
    df['word_bag'] = df[text_column].apply(text_to_bag)
    df['vector_representation'] = df['word_bag'].apply(get_vector_representation,
                                args=[model])
    return df

def get_vector_representation(bag, model):
    '''
    INPUT: string (bag) of words
    OUTPUT: Vector representation of input, using word2vec

    Note #1: see http://mccormickml.com/2016/04/12/googles-pretrained-word2vec-model-in-python/
    for how to download pre-trained Google word2Vec model and more details
    Note #2: This function gets the *average* vector representation for each bag
    of words. Whether or not this is the best algorithm to handle this data
    is open to interpretation.
    '''
    word_vect_list = []
    for word in bag.strip().split():
        try:
            wordvec = model[word]
            word_vect_list.append(wordvec)
        except KeyError:
            print(word, " not in vocabulary")
    return np.mean(np.array(word_vect_list), 0)


def get_video_url(vector, content_df, distance = 'cosine'):
    '''
    INPUT: vector of a question
    OUTPUT: KA URL most closely associated with the question vector
    '''
    min_dist = 2
    best_distance_url = 'www.google.com'

    for index, row in content_df.iterrows():
        kind = type(row['vector_representation'])
        if kind == str:
            print('String error')
        else:
            vect_dist = cdist(vector.reshape(1,-1),
                        row['vector_representation'].reshape(1,-1), distance)
            if vect_dist < min_dist:
                min_dist = vect_dist
                try:
                    best_distance_url = row['video_url']

                except KeyError:
                    print("Keyerror: \n", row)
    return best_distance_url


def question_to_relevant_videos(df, KA_content_df):
    '''
    INPUT: Pandas dataframes of questions and Khan Academy material
    OUTPUT: Questions pandas dataframe with column for closest video URL
    '''
    df['question_url'] = df['vector_representation'].apply(get_video_url,
                        args = [KA_content_df])
    return df


def get_students_data(filename):
    '''
    INPUT: csv file with student names, emails, and (raw) scores on each
    OUTPUT: dictionary, with email as key and list as value (as requested by Kevin)
    '''
    student_dict = {}
    df = pd.read_csv(filename)
    for _, row in df.iterrows():
        student_dict[row['email']] = [row['name'], list(row[2:].values)] # note structure
    return student_dict


def get_video_feedback(student_dict, weight_array, content_df):
    '''
    INPUT: dictionary from get_students_data, numpy array of how much each question is worth
    OUTPUT: dictionary with lists as values containing URLs of review videos
    '''
    video_list = content_df.video_url
    for student in student_dict.keys():
        scores = student_dict[student][1]/weight_array
        questions_to_review = [i for i, j in enumerate(scores) if j < .75]
        if not questions_to_review:
            student_videos = ['https://www.khanacademy.org/math/differential-equations/laplace-transform']
        else:
            student_videos = [video_list[i] for i in questions_to_review]
        student_dict[student].append(student_videos)
    return student_dict


def load_word2vec_model():
    '''
    Returns word2vec model if not already in working environment
    '''
    try:
        word2vec_model
    except:
        print('Loading pre-trained word2vec model!')
        return gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)


def send_emails(student_dict):
    '''
    INPUT: Dictionary of student data
    OUTPUT: None (emails sent)
    '''
    for student_email in student_dict.keys():
        sendEmail(student_dict[student_email][0], student_email,
                    student_dict[student_email][2])

def pickle_saver(filename, df):
    '''
    Save to dataframe to filename
    '''
    with open(filename, 'wb') as f:
        pickle.dump(df, f, pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    # Load in question and Khan Academy data
    question_df = read_questions('math_output.csv')
    khan_academy_df = load_KA_content(['khan_academy_bagged_df.csv', 'High_School_Math_Material_df'])

    # Load in model if not already present in workspace
    word2vec_model = load_word2vec_model()

    # Get bag of words for questions and vector representation
    question_df = document_to_bags_and_vector(question_df, 'question',
                    word2vec_model)
    # If needed, get vector representation of KA material, save object
    if 'vector_representation' not in khan_academy_df.columns:
        khan_academy_df = document_to_bags_and_vector(khan_academy_df,
                                                    'video_description',
                                                      word2vec_model)
        khan_academy_df.to_csv('khan_academy_bagged_df.csv')

    # Get column of corresponding video URLs for each question
    question_df = question_to_relevant_videos(question_df, khan_academy_df)

    # Get student name, email, and test scores in dictionary
    student_dict = get_students_data('student.csv')

    # Score each student, assign videos for questions they did poorly on
    student_dict = get_video_feedback(student_dict, np.array([10]*10), khan_academy_df)

    # Send customized emails to each student
    send_emails(student_dict)
