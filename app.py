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
    left_pitch  = request.form['left_pitch']
    right_pitch = request.form['right_pitch']

    pitches = app.config['PITCHES']

    if (left_pitch not in pitches) or (right_pitch not in pitches):
        return "invalid request parameter"

    modules = get_modules(left_pitch, right_pitch)
    return modules

    if left_pitch != str(modules['left']['pitch']):
        return 'left pitch requires update'
        # return update_firmware(modules['left']['mac'], left_pitch)
    if right_pitch != str(modules['right']['pitch']):
        return 'right pitch requires update'
        # return update_firmware(modules['right']['mac'], right_pitch)
    return 'program finished'

@app.route('/firm')
# def update_firmware(mac, pitch):
def update_firmware():
    firmware_file_names = app.config["FIRMWARE_FILES"]
    # return dumps(firmware_file_names)

    firmware_path = app.config["FIRMWARE_PATH"]
    fw = firmware_path + app.config["FF"]
    fileContent = open(fw, 'rb').read()

    mac = "00:18:B7:89:45:78"

    # "mac": "00:18:B7:09:45:40"
    # "mac": "00:18:B7:08:07:06",

    auth_token = app.config["AUTH_TOKEN"]
    url = 'http://' + app.config["IP_ADDRESS"] + '/api/devices?command=update-firmware'

    #MultipartEncoder explained in https://stackoverflow.com/a/12385661
    mp_encoder = MultipartEncoder(
        fields={
            'ids': mac,
            'file': (app.config["FF"], open(fw, 'rb'), 'application/octet-stream'),
        }
    )
    r = requests.post(
        url,
        data=mp_encoder,
        headers={'Content-Type': mp_encoder.content_type, 'Authorization' : 'Bearer ' + auth_token}
    )
    return r.content

@app.route('/reboot-devices')
def reboot_devices(macs):
    url = '/api/devices?command=reboot'
    headers = {'Authorization': 'Bearer ' + app.config["AUTH_TOKEN"]}
    r = requests.post(url, data = {'ids':macs}, headers=headers)
    return 'rebooting macs'

#patching modules with new dimensions
@app.route('/patch-video-server')
def patch_video_server():
    url = '/api/video-servers/0'
    http_method = 'PATCH'
    return 'patching modules(offset/wid/hight)'

#Restarts the controller to apply any changes made to the configuration.
@app.route('/restart-controller')
def restart_controller():
    url = '/api/controllers/0?command=restart'
    headers = {'Authorization': 'Bearer ' + app.config["AUTH_TOKEN"]}
    r = requests.post(url, headers=headers)

    return "restarting the controller"

#Patch layouts for left/right
@app.route('/patch-layouts')
def patch_layouts():
    #TODO define URL
    return 'patching layouts'

#Restarting the Scheduler.
@app.route('/restart-scheduler')
def restart_scheduler():
    url = '/api/schedulers/0?command=restart'
    return "Restarting the Scheduler."

@app.route('/modules')
def get_modules(left_pitch, right_pitch):
    ip = app.config["IP_ADDRESS"]

    api_route = "/api/devices"
    response = requests.get('http://' + ip + api_route).json()
    # return dumps(response['data'])

    panel_ids = app.config["PANEL_IDS"]
    for device in response['data']:
        device_class = device['attributes']['device-class']
        # if device_class.startswith('TCO'):


    # return dumps(goodids)
    module_a = response#['data']#[0]#['attributes']
    return module_a
    module_b = response['data'][1]#['attributes']
    return module_b
    module_c = response['data'][2]['attributes']
    return module_c


    if module_a['offset']['x'] < module_b['offset']['x']:
        module_a_side = 'left'
        module_b_side = 'right'
    else:
        module_a_side = 'right'
        module_b_side = 'left'

    modules = {}
    pitch_dimensions = app.config["PIXEL_TO_PITCH"]

    modules[module_a_side] = {
        #'pitch': pitch_dimensions[module_a['size']['width']],
        'mac': module_a['mac']
    }
    modules[module_b_side] = {
        #'pitch': pitch_dimensions[module_b['size']['width']],
        'mac': module_b['mac']
    }

    return modules



