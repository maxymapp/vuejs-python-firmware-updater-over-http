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

@app.route('/config')
def getConfig():
    r = requests.get('http://10.0.0.3/api/modules')
    rdata = r.json()

    sizes = {}
    sizes['left'] = rdata['data'][1]['attributes']['size']
    sizes['right'] = rdata['data'][0]['attributes']['size']

    return sizes

#@app.route('/newdims')
def comparePitches(leftPitch, rightPitch):
    # extract selected pitch from requests
    # transform passed pitch to pixel dimensions
    # read current config
    # compare dimensions
    config = getConfig()

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

    #if newDimensions['left'] == config['left']
    return dumps(newDimensions)



'''


#@app.route('/tcauth', methods=['POST'])
#def getAuthToken():
    #headers = {"Authorization": "Bearer 23DE481ED297204C731E398DEAEA2770AF20E96EB84111FB"}

    #r = requests.post('http://10.0.0.3/api/token', data={'grant_type': 'password',})


'''




