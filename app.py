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

def get_devices():
    response = requests.get('http://' + app.config["IP_ADDRESS"] + "/api/devices").json()
    devices = {}
    for device in response['data']:
        device_class = device['attributes']['device-class']
        if device_class.startswith('TCO'):
            pitch = app.config["DEVICE_CLASS_TO_PITCH"][device_class]
            mac = device['attributes']['mac']
            devices[mac] = pitch
    return devices

@app.route('/modules')
def get_modules():
    devices = get_devices()

    response = requests.get('http://' + app.config["IP_ADDRESS"] + "/api/modules").json()

    if len(response['data']) < 2:
        return "either or both modules are not found"
    if len(response['data']) > 2:
        return "more than 2 modules are found"

    modules = {}
    for module in response['data']:
        mac = module['attributes']['mac']
        if mac == "00:18:B7:09:45:78":
            modules['left'] = {'mac': mac, 'pitch': str(devices[mac]), 'id': str(module['id'])}
        if mac == "00:18:B7:09:45:40":
            modules['right'] = {'mac': mac, 'pitch': str(devices[mac]), 'id': str(module['id'])}
    return modules

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
    id = request.form['id']
    url = 'http://' + app.config["IP_ADDRESS"] + '/api/devices?command=reboot'
    headers = {'Authorization': 'Bearer ' + app.config["AUTH_TOKEN"]}
    r = requests.post(url, data = {'ids': [id]}, headers=headers)
    return 'rebooting macs'

@app.route('/poll-reboot')
def poll_reboot():
    url = 'http://' + app.config["IP_ADDRESS"] + "/api/progresses?filter[type]=reboot-devices"
    headers = {'Authorization': 'Bearer ' + app.config["AUTH_TOKEN"]}

    r = requests.get(url, headers=headers)
    return r.content

@app.route('/patch-modules', methods=['POST'])
def patch_modules():
    pitch_to_dims = {
        '1.6': {'w': 192, 'h': 216},
        '2.0': {'w': 160, 'h': 180},
        '2.5': {'w': 128, 'h': 144},
        '4.0': {'w': 80, 'h': 90}
    }
    module_id = request.form['module_id']
    this_pitch = request.form['this_pitch']

    if "the_other_pitch" in request.form:
        the_other_pitch = request.form['the_other_pitch']
        offset_x = pitch_to_dims[the_other_pitch]['w']
    else:
        offset_x = 0

    data = {
        "data": {
            "type": "modules",
            "id": module_id,
            "attributes": {
                "offset": {
                    "x": offset_x,
                    "y": 0
                },
                "size": {
                    "width": pitch_to_dims[this_pitch]['w'],
                    "height": pitch_to_dims[this_pitch]['h']
                }
            }
        }
    }

    url = 'http://' + app.config["IP_ADDRESS"] + "/api/modules"
    headers = {'Authorization': 'Bearer ' + app.config["AUTH_TOKEN"]}
    r = requests.patch(url, dumps(data), headers=headers)
    return r.content

@app.route('/save-config', methods=['POST'])
def save_configuration():
    url = "http://" + app.config["IP_ADDRESS"] + "/api/controllers/0?command=save-sign-configuration"
    headers = {'Authorization': 'Bearer ' + app.config["AUTH_TOKEN"]}
    r = requests.post(url, headers=headers)
    return r.content

@app.route('/patch-layouts', methods=['POST'])
def patch_layouts():
    pitch_to_dims = {
        '1.6': {'w': 192, 'h': 216},
        '2.0': {'w': 160, 'h': 180},
        '2.5': {'w': 128, 'h': 144},
        '4.0': {'w': 80, 'h': 90}
    }
    module_id = request.form['module_id']
    this_pitch = request.form['this_pitch']

    if "the_other_pitch" in request.form:
        the_other_pitch = request.form['the_other_pitch']
        offset_x = pitch_to_dims[the_other_pitch]['w']
        layout_id = "0x8e26617cd8"
    else:
        offset_x = 0
        layout_id = "0x8e26617cd7"

    url = 'http://' + app.config["IP_ADDRESS"] + "/api/layouts/" + layout_id
    headers = {'Authorization': 'Bearer ' + app.config["AUTH_TOKEN"]}

    data = {
        "data": {
            "type": "layouts",
            "id": module_id,
            "attributes": {
                "position": {
                    "x": offset_x,
                    "y": 0
                },
                "size": {
                    "width": pitch_to_dims[this_pitch]['w'],
                    "height": pitch_to_dims[this_pitch]['h']
                }
            }
        }
    }
    return dumps(data)
    r = requests.patch(url, dumps(data), headers=headers)
    return r.content


@app.route('/restart-controller', methods=['POST'])
def restart_controller():
    url = 'http://' + app.config["IP_ADDRESS"] + '/api/controllers/0?command=restart'
    headers = {'Authorization': 'Bearer ' + app.config["AUTH_TOKEN"]}
    r = requests.post(url, headers=headers)
    return r.content

#Restarting the Scheduler.
@app.route('/restart-scheduler', methods=['POST'])
def restart_scheduler():
    url = 'http://' + app.config["IP_ADDRESS"] + '/api/schedulers/0?command=restart'
    headers = {'Authorization': 'Bearer ' + app.config["AUTH_TOKEN"]}
    r = requests.post(url, headers=headers)
    return r.content
