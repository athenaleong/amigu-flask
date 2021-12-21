from flask import Flask, json, send_from_directory, jsonify, request
from flask_cors import CORS
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import random 

load_dotenv()
app = Flask(__name__)
CORS(app)

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


@app.route("/newQuestions", methods=['POST'])
def newQuestion():
    #TODO: pull new qn --> axios on frontend --> save to local storage
    numQ = request.json.get('numQ')
    oldQ = request.json.get('oldQ')
    data = supabase.table('question').select('*').execute()['data']
    data = [i for i in data if i['id'] not in oldQ]
    newQ = random.sample(data, numQ)
    data = jsonify({'newQ': newQ})
    return data

@app.route("/updateTable", methods=['POST'])
def updateTable():
    payload = request.json.get('payload')
    data = supabase.table('question').insert(payload).execute()
    if len(data.get("data", [])) > 0:
        return 'success', 200
    else:
        return 'database error', 500