import cgi, requests, os
from pprint import pprint

from flask import Flask, render_template, request, jsonify
from flask.json import dumps

app = Flask('PitchUpdater')
app.config.from_pyfile('config.cfg')

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    leftPitch  = request.form['leftpitch']
    rightPitch = request.form['rightpitch']

    pitches = app.config["PITCHES"]
    if (leftPitch not in pitches) or (rightPitch not in pitches):
        return "invalid request parameter"

    modules = get_modules()
    #return modules

    if leftPitch != str(modules['left']['pitch']):
        #return 'left pitch requires update'
        return update_firmware(modules["left"])
    if rightPitch != str(modules['right']['pitch']):
        #return 'right pitch requires update'
        return update_firmware(modules['right'])
    return 'program finished'


    #return

@app.route('/firm')
def update_firmware(module):
    #return "in firm ware update"
    #return module

    ip = app.config["IP_ADDRESS"]
    auth_token = app.config["AUTH_TOKEN"]
    url = 'http://' + ip + '/api/devices?command=update-firmware'

    #response = requests.get('http://' + ip + '/api/modules').json()

    firmware_path = app.config["FIRMWARE_PATH"]
    #return dumps(firmware_path)

    firmware_file_name = app.config["FIRMWARE_FILES"][module["pitch"]]
    #return dumps(firmware_file_name)

    firmware_file = firmware_path + firmware_file_name
    #return dumps(firmware_file)

    payload = {
        "filename": firmware_file,
        "mac": [module['mac']],
    }
    #return dumps(payload)

    headers = {
        'Content-Type': "multipart/form-data",
        'Authorization': "Bearer " + auth_token
    }
    response = requests.request("POST", url, data=dumps(payload), headers=headers)

    return response.status_code

@app.route('/modules')
def get_modules():
    ip = app.config["IP_ADDRESS"]
    response = requests.get('http://' + ip + '/api/modules').json()

    moduleA = response['data'][0]['attributes']
    moduleB = response['data'][1]['attributes']

    modules = {}

    pitchDimensions = app.config["PIXEL_TO_PITCH"]

    if moduleA['offset']['x'] < moduleB['offset']['x']:
        modules['left'] = {
            'pitch': pitchDimensions[moduleA['size']['width']],
            'mac': moduleA['mac']
        }
        modules['right'] = {
            'pitch': pitchDimensions[moduleB['size']['width']],
            'mac': moduleB['mac']
        }
    #else:
        #TODO opposite complete

    return modules





