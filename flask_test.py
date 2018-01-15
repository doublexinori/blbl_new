from flask import Flask
from pymongo import MongoClient
import json
import collections

app = Flask(__name__)

date = ''
location = ''
name = ''


def read_mongo(date, location, name):
    client = MongoClient('localhost', 27017)
    db = client.suzhoumeng
    if date != '':
        result = db.data.find({'date': date})
        data = []
        for item in result:
            data.append(
                eval(str(item).replace('\'', '"').replace('ObjectId(', '').replace(')', '').replace('_', '')))
    elif location != '':
        result = db.data.find({'location': location})
        data = []
        for item in result:
            data.append(
                eval(str(item).replace('\'', '"').replace('ObjectId(', '').replace(')', '').replace('_', '')))
    elif name != '':
        result = db.data.find({'name': name})
        data = []
        for item in result:
            data.append(
                eval(str(item).replace('\'', '"').replace('ObjectId(', '').replace(')', '').replace('_', '')))
    if str(data).find('[]') != -1:
        return False
    else:
        return data


def read_new_mongo(date, location, name):
    client = MongoClient('localhost', 27017)
    db = client.suzhoumeng
    if date != '':
        result = db.data_new.find({'date': date})
        data = []
        for item in result:
            data.append(
                eval(str(item).replace('\'', '"').replace('ObjectId(', '').replace(')', '').replace('_', '')))
    elif location != '':
        result = db.data_new.find({'location': location})
        data = []
        for item in result:
            data.append(
                eval(str(item).replace('\'', '"').replace('ObjectId(', '').replace(')', '').replace('_', '')))
    elif name != '':
        result = db.data_new.find({'name': name})
        data = []
        for item in result:
            data.append(
                eval(str(item).replace('\'', '"').replace('ObjectId(', '').replace(')', '').replace('_', '')))
    if str(data).find('[]') != -1:
        return False
    else:
        return data


@app.route('/api/date/<string:date>', methods=['GET'])
def get_data_date(date):
    task = read_mongo(date, location, name)
    data = collections.OrderedDict()
    if task is False:
        data['message'] = 'failed'
    else:
        data['message'] = 'success'
        data['data'] = task
    return json.dumps(data, ensure_ascii=False)


@app.route('/api/location/<string:location>', methods=['GET'])
def get_data_location(location):
    task = read_mongo(date, location, name)
    data = collections.OrderedDict()
    if task is False:
        data['message'] = 'failed'
    else:
        data['message'] = 'success'
        data['data'] = task
    return json.dumps(data, ensure_ascii=False)


@app.route('/api/name/<string:name>', methods=['GET'])
def get_data_name(name):
    task = read_mongo(date, location, name)
    data = collections.OrderedDict()
    if task is False:
        data['message'] = 'failed'
    else:
        data['message'] = 'success'
        data['data'] = task
    return json.dumps(data, ensure_ascii=False)


@app.route('/api/date_new/<string:date>', methods=['GET'])
def get_data_new_date(date):
    task = read_new_mongo(date, location, name)
    data = collections.OrderedDict()
    if task is False:
        data['message'] = 'failed'
    else:
        data['message'] = 'success'
        data['data'] = task
    return json.dumps(data, ensure_ascii=False)


@app.route('/api/location_new/<string:location>', methods=['GET'])
def get_data_new_location(location):
    task = read_new_mongo(date, location, name)
    data = collections.OrderedDict()
    if task is False:
        data['message'] = 'failed'
    else:
        data['message'] = 'success'
        data['data'] = task
    return json.dumps(data, ensure_ascii=False)


@app.route('/api/name_new/<string:name>', methods=['GET'])
def get_data_new_name(name):
    task = read_new_mongo(date, location, name)
    data = collections.OrderedDict()
    if task is False:
        data['message'] = 'failed'
    else:
        data['message'] = 'success'
        data['data'] = task
    return json.dumps(data, ensure_ascii=False)


# @app.errorhandler(404)
# def not_found(error):
#     return make_response(({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True)
