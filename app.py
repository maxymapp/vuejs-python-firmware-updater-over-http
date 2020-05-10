import requests
from flask import Flask, render_template, request
from flask.json import dumps
from requests_toolbelt.multipart.encoder import MultipartEncoder

app = Flask('PitchUpdater')
app.config.from_pyfile('config.cfg')

PITCH_SIZES = (
    1.6,
    2.0,
    2.5,
    4.0
)

PIXEL_TO_PITCH = {
    192: 1.6,
    160: 2.0,
    128: 2.5,
    80: 4.0
}

PITCH_TO_DIMS = {
    '1.6': {'w': 192, 'h': 216},
    '2.0': {'w': 160, 'h': 180},
    '2.5': {'w': 128, 'h': 144},
    '4.0': {'w': 80, 'h': 90}
}

DEVICE_CLASS_TO_PITCH = {
    'TCO1_6_I': 1.6,
    'TCO2_0_I': 2.0,
    'TCO2_5_I': 2.5,
    'TCO4_0_I': 4.0
}

FIRMWARE_FILES = {
    "1.6": "TCO1_6_60Hz_Internal.d3",
    "2.0": "TCO2_0_60Hz_Internal.d3",
    "2.5": "TCO2_5_60Hz_Internal.d3",
    "4.0": "TCO4_0_60Hz_Internal.d3"
}


@app.route('/')
def hello():
    authorize()
    return render_template('index.html')

def authorize():
    url = 'http://' + app.config["IP_ADDRESS"] + "/api/token"
    data = {
        "password": app.config["PASSWORD"],
        "username": app.config["USERNAME"]
    }
    r = requests.post(url, data=data)

    token = r.json()['access_token']
    app.config["AUTH_TOKEN"] = token


def get_headers():
    return {'Authorization': 'Bearer ' + app.config["AUTH_TOKEN"]}

def get_devices():
    response = requests.get('http://' + app.config["IP_ADDRESS"] + "/api/devices", headers=get_headers()).json()
    devices = {}
    for device in response['data']:
        device_class = device['attributes']['device-class']
        if device_class.startswith('TCO'):
            pitch = DEVICE_CLASS_TO_PITCH[device_class]
            mac = device['attributes']['mac']
            devices[mac] = pitch
    return devices


@app.route('/modules')
def get_modules():
    devices = get_devices()
    response = requests.get('http://' + app.config["IP_ADDRESS"] + "/api/modules", headers=get_headers()).json()

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
    firmware_file = FIRMWARE_FILES[pitch]
    fw = firmware_path + firmware_file
    # return dumps(fw)

    url = 'http://' + app.config["IP_ADDRESS"] + '/api/devices?command=update-firmware'

    # MultipartEncoder explained in https://stackoverflow.com/a/12385661
    mp_encoder = MultipartEncoder(
        fields={
            'ids': mac,
            'file': (firmware_file, open(fw, 'rb'), 'application/octet-stream'),
        }
    )
    headers = {
        'Content-Type': mp_encoder.content_type,
        'Authorization': 'Bearer ' + app.config["AUTH_TOKEN"]
    }
    r = requests.post(
        url,
        data=mp_encoder,
        headers=headers
    )
    return dumps(r.status_code)


@app.route('/poll-firmware-update')
def poll_firmware_update():
    url = 'http://' + app.config["IP_ADDRESS"] + "/api/progresses?filter[type]=firmware-update"

    r = requests.get(url, headers=get_headers())
    return r.content


@app.route('/reboot-devices', methods=["POST"])
def reboot_devices():
    id = request.form['id']
    url = 'http://' + app.config["IP_ADDRESS"] + '/api/devices?command=reboot'
    r = requests.post(url, data={'ids': [id]}, headers=get_headers())
    return 'rebooting macs'


@app.route('/poll-reboot')
def poll_reboot():
    url = 'http://' + app.config["IP_ADDRESS"] + "/api/progresses?filter[type]=reboot-devices"

    r = requests.get(url, headers=get_headers())
    return r.content


@app.route('/patch-modules', methods=['POST'])
def patch_modules():
    module_id = request.form['module_id']
    new_pitch = request.form['new_pitch']

    if "left_offset_pitch" in request.form:
        left_offset_pitch = request.form['left_offset_pitch']
        offset_x = PITCH_TO_DIMS[left_offset_pitch]['w']
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
                    "width": PITCH_TO_DIMS[new_pitch]['w'],
                    "height": PITCH_TO_DIMS[new_pitch]['h']
                }
            }
        }
    }

    url = 'http://' + app.config["IP_ADDRESS"] + "/api/modules"
    r = requests.patch(url, dumps(data), headers=get_headers())
    return r.content


@app.route('/save-config', methods=['POST'])
def save_configuration():
    url = "http://" + app.config["IP_ADDRESS"] + "/api/controllers/0?command=save-sign-configuration"
    r = requests.post(url, headers=get_headers())
    return r.content


@app.route('/patch-layouts', methods=['POST'])
def patch_layouts():
    new_pitch = request.form['new_pitch']
    layout_id = ""

    if "left_offset_pitch" in request.form:
        left_offset_pitch = request.form['left_offset_pitch']
        offset_x = PITCH_TO_DIMS[left_offset_pitch]['w']
        # TODO move layout ids to configuration file
        layout_id = "0x8e26617cd8"
    else:
        offset_x = 0
        layout_id = "0x8e26617cd7"

    url = 'http://' + app.config["IP_ADDRESS"] + "/api/layouts/" + layout_id

    data = {
        "data": {
            "type": "layouts",
            "id": layout_id,
            "attributes": {
                "position": {
                    "x": offset_x,
                    "y": 0
                },
                "size": {
                    "width": PITCH_TO_DIMS[new_pitch]['w'],
                    "height": PITCH_TO_DIMS[new_pitch]['h']
                }
            }
        }
    }
    # return dumps(data)
    r = requests.patch(url, dumps(data), headers=get_headers())
    return r.content


@app.route('/restart-controller', methods=['POST'])
def restart_controller():
    url = 'http://' + app.config["IP_ADDRESS"] + '/api/controllers/0?command=restart'
    r = requests.post(url, headers=get_headers())
    return r.content


# Restarting the Scheduler.
@app.route('/restart-scheduler', methods=['POST'])
def restart_scheduler():
    url = 'http://' + app.config["IP_ADDRESS"] + '/api/schedulers/0?command=restart'
    r = requests.post(url, headers=get_headers())
    return r.content
