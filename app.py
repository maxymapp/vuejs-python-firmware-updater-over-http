import cgi, requests, os, pycurl, array, uuid, re, base64
from urllib.parse import urlencode, quote_plus
from requests_toolbelt.multipart.encoder import MultipartEncoder
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
    left_pitch  = float(request.form['left-pitch'])
    right_pitch = float(request.form['right-pitch'])

    if (left_pitch not in app.config['PITCH_SIZES']) or (right_pitch not in app.config['PITCH_SIZES']):
        #TODO need frontend error?
        return "invalid request parameter"

    # return "nothing to update"
    # return dumps(modules)
    # if modules != []:
    #     for module in modules:
    #         return update_firmware(module)

    return 'program finished'

@app.route('/modules')
def get_modules():
    response = requests.get('http://' + app.config["IP_ADDRESS"] + "/api/devices").json()
    devices = {}
    for device in response['data']:
        device_class = device['attributes']['device-class']
        if device_class.startswith('TCO'):
            pitch = app.config["DEVICE_CLASS_TO_PITCH"][device_class]
            mac = device['attributes']['mac']
            devices[mac] = pitch

    response = requests.get('http://' + app.config["IP_ADDRESS"] + "/api/modules").json()

    if len(response['data']) < 2:
        return "either or both modules are not found"
    if len(response['data']) > 2:
        return "more than 2 modules are found"

    modules = {}
    for module in response['data']:
        if module['attributes']['offset']['x'] == 0:
            mac = module['attributes']['mac']
            modules['left'] = {'mac': mac, 'pitch': str(devices[mac]), 'id': str(module['id'])}
        if module['attributes']['offset']['x'] > 0:
            mac = module['attributes']['mac']
            modules['right'] = {'mac': mac, 'pitch': str(devices[mac]), 'id': str(module['id'])}
    return jsonify(modules)

@app.route('/update-firmware', methods=['POST'])
def update_firmware():
    mac = request.form['mac']
    pitch = request.form['pitch']

    firmware_path = app.config["FIRMWARE_PATH"]
    firmware_file = app.config["FIRMWARE_FILES"][pitch]
    fw = firmware_path + firmware_file
    # return dumps(fw)

    auth_token = app.config["AUTH_TOKEN"]
    url = 'http://' + app.config["IP_ADDRESS"] + '/api/devices?command=update-firmware'

    #MultipartEncoder explained in https://stackoverflow.com/a/12385661
    mp_encoder = MultipartEncoder(
        fields={
            'ids': mac,
            'file': (firmware_file, open(fw, 'rb'), 'application/octet-stream'),
        }
    )
    r = requests.post(
        url,
        data=mp_encoder,
        headers={'Content-Type': mp_encoder.content_type, 'Authorization' : 'Bearer ' + auth_token}
    )
    return dumps(r.status_code)

@app.route('/poll-firmware-update')
def poll_firmware_update():
    url = 'http://' + app.config["IP_ADDRESS"] + "/api/progresses?filter[type]=firmware-update"
    headers = {'Authorization': 'Bearer ' + app.config["AUTH_TOKEN"]}

    r = requests.get(url, headers=headers)
    return r.content

@app.route('/reboot-devices', methods=["POST"])
def reboot_devices():
    macs = request.form['mac']
    url = 'http://' + app.config["IP_ADDRESS"] + '/api/devices?command=reboot'
    headers = {'Authorization': 'Bearer ' + app.config["AUTH_TOKEN"]}
    r = requests.post(url, data = {'ids':macs}, headers=headers)
    return 'rebooting macs'

#3
# patch to /api/modules to update the offset and size.  Here is the json for that:
@app.route('/patch-modules')
def patch_modules(macs):
    uri = "/api/modules"
    method = "PATCH"
    return "patching modules"

# {
#   "data": {
#     "type": "modules",
#     "id": "69798",
#     "attributes": {
#       "offset": {
#         "x": 1000,
#         "y": 20
#       },
#       "size": {
# 	"width": 440,
# 	"height": 280
#         }
#     }
#   }
# }

#Patch layouts
@app.route('/patch-layouts')
def patch_layouts():
    uri = "/api/layouts/0"
    method = "PATCH"
    return 'patching layouts'

#Restarts the controller to apply any changes made to the configuration.
@app.route('/restart-controller')
def restart_controller():
    url = '/api/controllers/0?command=restart'
    headers = {'Authorization': 'Bearer ' + app.config["AUTH_TOKEN"]}
    r = requests.post(url, headers=headers)

    return "restarting the controller"

#Restarting the Scheduler.
@app.route('/restart-scheduler')
def restart_scheduler():
    url = '/api/schedulers/0?command=restart'
    return "Restarting the Scheduler."
