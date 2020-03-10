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
    #if request.method == 'POST':
    return comparePitches(request.form['leftpitch'], request.form['rightpitch'])

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

    return

#@app.route('/newdims')
def comparePitches(leftPitch, rightPitch):

    currentDimensions = getCurrentDimensions()

    pitchDimensions = {
        '1.6': {
            'height': 216,
            'width': 192
        },
        '2.0': {
            'height': 180,
            'width': 160
        },
        '2.5': {
            'height': 144,
            'width': 128
        },
        '4.0': {
            'height': 90,
            'width': 80
        }
    }

    newDimensions = {}
    newDimensions['left'] = pitchDimensions[leftPitch]
    newDimensions['right'] = pitchDimensions[rightPitch]

    #macLeft =
    #macRight =

    if newDimensions['left']['height'] == currentDimensions['left']['height']:
        updateFirmware(currentDimensions["left"]["mac"])

    return dumps(newDimensions)

@app.route('/config')
def getCurrentDimensions():
    response = requests.get('http://10.0.0.3/api/modules').json()

    moduleA = response['data'][0]['attributes']
    moduleB = response['data'][1]['attributes']

    modules = {}

    if moduleA['offset']['x'] < moduleB['offset']['x']:
        modules['left'] = moduleA['size']
        modules['left']['mac'] = moduleA['mac']
        modules['right'] = moduleB['size']
        modules['right']['mac'] = moduleB['mac']

    else:
        modules['left'] = moduleB['size']
        modules['left']['mac'] = moduleB['mac']
        modules['right'] = moduleA['size']
        modules['right']['mac'] = moduleA['mac']

    return modules

'''


#@app.route('/tcauth', methods=['POST'])
#def getAuthToken():
    #headers = {"Authorization": "Bearer 23DE481ED297204C731E398DEAEA2770AF20E96EB84111FB"}

    #r = requests.post('http://10.0.0.3/api/token', data={'grant_type': 'password',})


'''




