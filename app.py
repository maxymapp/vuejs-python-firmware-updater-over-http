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
    left_pitch  = request.form['leftpitch']
    right_pitch = request.form['rightpitch']

    pitches = app.config['PITCHES']

    if (left_pitch not in pitches) or (right_pitch not in pitches):
        return "invalid request parameter"

    modules = get_modules()
    #return modules

    if left_pitch != str(modules['left']['pitch']):
        #return 'left pitch requires update'
        update_firmware(modules['left']['mac'], left_pitch)
    if right_pitch != str(modules['right']['pitch']):
        #return 'right pitch requires update'
        update_firmware(modules['right']['mac'], right_pitch)
    return 'program finished'

@app.route('/firm')
def update_firmware(mac, pitch):
    ip  = app.config["IP_ADDRESS"]
    url = 'http://' + ip + '/api/devices?command=update-firmware'
    auth_token = app.config["AUTH_TOKEN"]

    firmware_path = app.config["FIRMWARE_PATH"]
    #return dumps(firmware_path)

    firmware_file_name = app.config["FIRMWARE_FILES"][pitch]
    #return dumps(firmware_file_name)

    firmware_file = firmware_path + firmware_file_name
    #return dumps(firmware_file)

    payload = {
        "filename": firmware_file,
        "mac": [mac]
    }

    headers = {
        'Content-Type': "multipart/form-data",
        'Authorization': "Bearer " + auth_token
    }
    response = requests.post(url, files=dict(payload))

    return response.status_code

@app.route('/modules')
def get_modules():
    ip = app.config["IP_ADDRESS"]
    response = requests.get('http://' + ip + '/api/modules').json()

    module_a = response['data'][0]['attributes']
    module_b = response['data'][1]['attributes']

    if module_a['offset']['x'] < module_b['offset']['x']:
        module_a_side = 'left'
        module_b_side = 'right'
    else:
        module_a_side = 'right'
        module_b_side = 'left'

    modules = {}
    pitch_dimensions = app.config["PIXEL_TO_PITCH"]

    modules[module_a_side] = {
        'pitch': pitch_dimensions[module_a['size']['width']],
        'mac': module_a['mac']
    }
    modules[module_b_side] = {
        'pitch': pitch_dimensions[module_b['size']['width']],
        'mac': module_b['mac']
    }

    return modules





