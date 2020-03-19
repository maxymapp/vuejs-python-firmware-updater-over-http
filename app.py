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

    modules = get_modules_to_update(left_pitch, right_pitch)
    # return "nothing to update"
    # return dumps(modules)
    if modules != []:
        for module in modules:
            return update_firmware(module)

    return 'program finished'

@app.route('/firm')
# def update_firmware(mac, pitch):
def update_firmware(module):
    # return dumps(module)

    firmware_path = app.config["FIRMWARE_PATH"]
    firmware_file = app.config["FIRMWARE_FILES"][module['pitch']]
    fw = firmware_path + firmware_file
    # return dumps(fw)

    auth_token = app.config["AUTH_TOKEN"]
    url = 'http://' + app.config["IP_ADDRESS"] + '/api/devices?command=update-firmware'

    #MultipartEncoder explained in https://stackoverflow.com/a/12385661
    mp_encoder = MultipartEncoder(
        fields={
            'ids': module['mac'],
            'file': (firmware_file, open(fw, 'rb'), 'application/octet-stream'),
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
def get_modules_to_update(left_pitch, right_pitch):
    response = requests.get('http://' + app.config["IP_ADDRESS"] + "/api/devices").json()
    # return dumps(response['data'])

    devices = {}
    for device in response['data']:
        device_class = device['attributes']['device-class']
        if device_class.startswith('TCO'):
            mac = device['attributes']['mac']
            devices[mac] = app.config["DEVICE_CLASS_TO_PITCH"][device_class]

    # return devices

    response = requests.get('http://' + app.config["IP_ADDRESS"] + "/api/modules").json()
    # return dumps(response['data'])

    if len(response['data']) < 2:
        return "either or both modules are not found"
    if len(response['data']) > 2:
        return "more than 2 modules are found"

    modules_to_update = []
    for module in response['data']:
        if(module['attributes']['offset']['x'] == 0):
            mac = module['attributes']['mac']
            if devices[mac] != float(left_pitch):
                # return mac
                modules_to_update.append({'mac': mac, 'pitch': left_pitch})
                # update_firmware()
        if (module['attributes']['offset']['x'] > 0):
            mac = module['attributes']['mac']
            if devices[mac] != float(right_pitch):
                # update_firmware()
                # return mac
                modules_to_update.append({'mac': mac, 'pitch': right_pitch})

    return modules_to_update



