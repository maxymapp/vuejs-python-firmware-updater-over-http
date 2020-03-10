import cgi, requests
from pprint import pprint

from flask import Flask, render_template, request, jsonify
from flask.json import dumps

app = Flask('PitchUpdater')

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    leftPitch  = request.form['leftpitch']
    rightPitch = request.form['rightpitch']

    pitches = ('1.6', '2.0', '2.5', '4.0')

    #update config
    #update firmware

    #return


def updateFirmware(mac, firmwareFile):
    #TODO read token from config file not committed to GIT
    ip  = "10.0.0.3"
    url = 'http://' + ip + '/api/devices?command=update-firmware'

    payload = {
        "filename": firmwareFile,
        "macs": mac,
    }
    headers = {
        'Content-Type': "application/json",
        #'Authorization': "Bearer " + token
    }
    requests.request("POST", url, data=dumps(payload), headers=headers)

    #return

@app.route('/modules')
def get_modules():
    response = requests.get('http://10.0.0.3/api/modules').json()

    moduleA = response['data'][0]['attributes']
    moduleB = response['data'][1]['attributes']

    modules = {}

    pitchDimensions = {
        192: 1.6,
        160: 2.0,
        128: 2.5,
         80: 4.0
    }

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

'''


#@app.route('/tcauth', methods=['POST'])
#def getAuthToken():
    #headers = {"Authorization": "Bearer 23DE481ED297204C731E398DEAEA2770AF20E96EB84111FB"}

    #r = requests.post('http://10.0.0.3/api/token', data={'grant_type': 'password',})


'''




