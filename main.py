from flask import Flask, json, send_from_directory, jsonify, request
from flask_cors import CORS
# from flask_caching import Cache
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import random 


load_dotenv()

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
app = Flask(__name__)
CORS(app)
# app.config.from_mapping(config)
# cache = Cache(app)
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


@app.route("/newQuestions", methods=['POST'])
def newQuestions():
    #TODO: pull new qn --> axios on frontend --> save to local storage
    #TODO: make this algo better lol it is so inefficient rn
    numQ = request.json.get('numQ')
    oldQ = request.json.get('oldQ')
    data = supabase.table('question').select('*').execute()['data']
    data = [i for i in data if i['id'] not in oldQ]
    newQ = random.sample(data, numQ)
    data = jsonify({'newQ': newQ})
    return data

@app.route("/allQuestions", methods=["GET"])
# @cache.cached(timeout=3600)
#PROGRAMMER NOTE: select from supabase --> create json file --> set up cache --> check eveyrthing in page works --> move on to pet
def allQuestions():
    data = supabase.table('category').select('name').execute()['data']
    category = [d['name'] for d in data]
    payload = []
    for c in category:
        questions = supabase.table('question').select('content', 'id').eq('category', c).execute()['data']
        payload.append({'category': c, 'questions': questions})
    data = jsonify({'payload': payload})
    return data



@app.route("/updateTable", methods=['POST'])
def updateTable():
    payload = request.json.get('payload')

    #Implemeted try-except since delete function yield unknown error
    try:
        result = supabase.table('question').delete().execute()
    except Exception as e:
        pass

    data = supabase.table('question').insert(payload).execute()
    if len(data.get("data", [])) > 0:
        return 'success', 200
    else:
        return 'database error', 500
    return 'success', 200

