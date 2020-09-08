import pandas as pd
import numpy as np
import operator
from flask import Flask, jsonify, request
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer
nltk.download('punkt') # if necessary...
stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]

'''remove punctuation, lowercase, stem'''
def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')

def cosine_sim(text1, text2):
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]



def supply_demand(my_demand, my_location):
    demand = pd.read_excel('demand.xlsx')
    supply = pd.read_excel('supply.xlsx')
    demand = pd.DataFrame(demand)
    supply = pd.DataFrame(supply)
    data = {}
    senetnces = []
    if my_demand:
        print("Sentence = ",my_demand)
        print()
        for i in range(0,len(supply.supply)):
            data[supply.supply[i]] = cosine_sim(my_demand,supply.supply[i])
    sorted_d = dict(sorted(data.items(), key=operator.itemgetter(1),reverse=True))
    threshold = 0.2
    s = []
    for i in sorted_d.items():
        if i[1] > threshold:
            s.append(i[0])
    s_rows = []
    for i in range(len(supply)):
        if supply.iloc[i]['supply'] in s:
            s_rows.append(i)
        elif supply.iloc[i]['location'] in my_location:
            s_rows.append(i)
    final_d = supply.iloc[s_rows]
    result = []
    print(result)
    for i in range(len(final_d)):
        result.append({"Supply":final_d.iloc[i]['supply'],"Location":final_d.iloc[i]['location'],"Date Posted":final_d.iloc[i]['date']})
    print("-------")
    print(result)
    result.append({"demand_asked": my_demand})
    return result

@app.route('/co19/supply_demand_route', methods=['POST'])
def supply_demand_route():
    #GET THE POSTED DATA
    posteddata = request.get_json()
    #READING THE DATA
    my_demand = str.lower(posteddata["my_demand"])
    my_location = str.lower(posteddata["my_location"]) 
    res = supply_demand(my_demand, my_location)
    final_return_message = {
            "related_supply":res,
            "status":200  # If already exists
            }
    return jsonify(final_return_message)


@app.route('/co19/areas', methods=['GET'])
def areas():
    supply = pd.read_excel('supply.xlsx')
    supply = pd.DataFrame(supply)
    areas = supply['location'].unique()
    areas = [i.title() for i in areas]
    final_return_message = {
            "areas":areas,
            "status":200  # If already exists
            }
    return jsonify(final_return_message)



#app.run
if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)