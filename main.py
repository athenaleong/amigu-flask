from flask import Flask, json, send_from_directory, jsonify, request
from flask_cors import CORS
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import random 
from flask_caching import Cache


load_dotenv()

# config = {
#     "DEBUG": True,          # some Flask specific configs
#     "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
#     "CACHE_DEFAULT_TIMEOUT": 300
# }
app = Flask(__name__)
CORS(app)
cache = Cache()
# app.config.from_mapping(config)
cache_servers = os.environ.get('MEMCACHIER_SERVERS')
if cache_servers == None:
    print('not caching')
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})
else:
    print('caching')
    cache_user = os.environ.get('MEMCACHIER_USERNAME') or ''
    cache_pass = os.environ.get('MEMCACHIER_PASSWORD') or ''
    cache.init_app(app,
        config={'CACHE_TYPE': 'saslmemcached',
                'CACHE_MEMCACHED_SERVERS': cache_servers.split(','),
                'CACHE_MEMCACHED_USERNAME': cache_user,
                'CACHE_MEMCACHED_PASSWORD': cache_pass,
                'CACHE_DEFAULT_TIMEOUT': 3600,
                'CACHE_OPTIONS': { 'behaviors': {
                    # Faster IO
                    'tcp_nodelay': True,
                    # Keep connection alive
                    'tcp_keepalive': True,
                    # Timeout for set/get requests
                    'connect_timeout': 2000, # ms
                    'send_timeout': 750 * 1000, # us
                    'receive_timeout': 750 * 1000, # us
                    '_poll_timeout': 2000, # ms
                    # Better failover
                    'ketama': True,
                    'remove_failed': 1,
                    'retry_timeout': 2,
                    'dead_timeout': 30}}})
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


@app.route("/newQuestions", methods=['POST'])
def newQuestions():
    #NOTE: slow runtime
    numQ = request.json.get('numQ')
    oldQ = request.json.get('usedQ')
    data = supabase.table('question').select('*').execute()['data']
    data = [i for i in data if i['id'] not in oldQ]
    newQ = random.sample(data, numQ)
    data = jsonify({'newQ': newQ})
    return data

@app.route("/allQuestions", methods=["GET"])
@cache.cached(timeout=3600)
def allQuestions():
    data = supabase.table('category').select('name').execute()['data']
    category = [d['name'] for d in data]
    payload = []
    for c in category:
        questions = supabase.table('question').select('*').eq('category', c).execute()['data']
        payload.append({'category': c, 'questions': questions})
    data = jsonify({'payload': payload})
    return data

@app.route("/updateTable", methods=['POST'])
def updateTable():
    payload = request.json.get('payload')
    tableName = request.json.get('tableName')

    #Implemeted try-except since delete function yield unknown error
    try:
        result = supabase.table(tableName).delete().execute()
    except Exception as e:
        pass

    print(tableName)
    data = supabase.table(tableName).insert(payload).execute()
    print(data)

    if data.get("status_code") != 201:
        return 'database error', data.get("status_code")
    
    if len(data.get("data", [])) > 0:
        return 'success', 200
    else:
        return 'database error', 500

@app.route("/allTreasures", methods=['GET'])
@cache.cached(timeout=3600)
def allTreasures():
    treasureType = supabase.table('treasure').select('type').execute()['data']
    treasureType = [d['type'] for d in treasureType]
    treasureType = list(dict.fromkeys(treasureType))
    payload = []
    for t in treasureType:
        data = supabase.table('treasure').select('*').eq('type', t).execute()['data']
        entry = {'type': t, 'idToInfo': data}
        payload.append(entry)
    data = jsonify({'payload': payload})
    return data

@app.route('/newTreasures', methods=['POST'])
def newTreasures():
    length = int(request.json.get('length'))
    treasure = request.json.get('oldTreasure')
    oldTreasure = []
    for v in list(treasure.values()):
        oldTreasure.extend(v)

    payload = supabase.table('treasure').select('id').execute()['data']
    payload = [i['id'] for i in payload if i['id'] not in oldTreasure]
    newTreasure = random.sample(payload, length)
    data = jsonify({'newTreasure': newTreasure})

    return data

@app.route('/treasureDetail', methods=['GET'])
def treasureDetails():
    id = request.args.get('id')
    data = supabase.table('treasure').select('*').eq('id', id).execute()['data']
    return jsonify({'payload': data[0]})


@app.route('/questionIdToData', methods=['POST'])
def questionIdToInfo():
    id = request.json.get('id')
    payload = []
    for i in id:
        print(i)
        data = supabase.table('question').select('*').eq('id', str(i)).execute()['data']
        if len(data):
            payload.append(data)

    return jsonify({'payload': payload})

# @app.route('/allCategories', methods=['GET'])
# @cache.cached(timeout=3600)







