'''
Author: Zachary Thomas
Scripts pulls in video information from Khan Academy API, saves
relevant information to file 
'''

import pandas as pd
import json
import urllib.request
try:
    import cPickle as pickle
except:
    import pickle


def get_topic_json(filename=None):
    '''
    INPUT: (optional) file location of pickled json object
    OUTPUT: json object featuring Khan Academy topic data
    '''
    if not filename: #Pull in data from internet if file location not specified
        print('Loading from Khan Academy API -- this will take a minute')
        connection = urllib.request.urlopen('http://www.khanacademy.org/api/v1/topictree?kind=Topic')
        js = connection.read()
        topic_json = json.loads(js.decode("utf-8"))
        with open('json_obj', 'wb') as f:
            pickle.dump(topic_json, f, pickle.HIGHEST_PROTOCOL)
        return topic_json
    else:
        return pickle.load(open(filename, "rb"))


def build_data_frame(json_obj, category_dict):
    '''
    INPUT: json object, dictionary of domain names and corresponding standalone titles
    OUTPUT: Pandas DataFrame with columns for video title, description and URL
    '''
    # Sorry for how messy this looks -- blame the structure of the JSON spit out by the KA API
    df = pd.DataFrame()
    for domain_slug in category_dict.keys():
        domain_index = [item['domain_slug'] for item in json_obj['children']].index(domain_slug)
        print(domain_slug, ' ', domain_index)
        for standalone_title in category_dict[domain_slug]:
            print(standalone_title)
            st_index = [item['standalone_title'] for item in json_obj['children'][domain_index]['children']].index(standalone_title)
            for unit in json_obj['children'][domain_index]['children'][st_index]['children']:
                for lesson in unit['children']:
                    data = pd.DataFrame({"video_title": lesson['title'], "video_description": lesson['description'], "video_url": lesson['ka_url']}, index=[0])
                    df = df.append(data, ignore_index=True)
    return df

def save_topic_df(filename, df):
    '''
    Save to topic dataframe to filename
    '''
    with open(filename, 'wb') as f:
        pickle.dump(df, f, pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    topic_json = get_topic_json('json_object')

    #Create category dict. As currently structured, each domain has a list of standalone titles
    category_dict = {}
    standalone_title_list = ['Algebra', 'Algebra basics','Algebra I',
    'Algebra II', 'Geometry', 'Basic geometry', 'High school geometry',
    'Trigonometry', 'Precalculus', 'AP Calculus AB', 'AP Calculus BC',
    'Linear algebra']
    category_dict['math'] = standalone_title_list

    #Get and save dataframe of Khan Academy text and URLs
    topic_df = build_data_frame(topic_json, category_dict)
    save_topic_df('High_School_Math_Material_df', topic_df)
