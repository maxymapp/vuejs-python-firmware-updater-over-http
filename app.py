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
    left_pitch  = request.form['leftpitch']
    right_pitch = request.form['rightpitch']

    pitches = app.config['PITCHES']

    if (left_pitch not in pitches) or (right_pitch not in pitches):
        return "invalid request parameter"

    modules = get_modules()
    #return modules

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
    pitch = '4.0'
    firmware_file_name = app.config["FIRMWARE_FILES"][pitch]
    firmware_file_name_no_ext = re.sub('\.d3$', '', firmware_file_name)
    # return firmware_file_name
    firmware_path = app.config["FIRMWARE_PATH"]
    # return (firmware_path)
    firmware_file = firmware_path + firmware_file_name
    # return (firmware_file)

    boundary = "--" + str(uuid.uuid1().int)
    eol = "\r\n"

    auth_token = app.config["AUTH_TOKEN"]
    url = 'http://' + app.config["IP_ADDRESS"] + '/api/devices?command=update-firmware'

    # headers = [
    #     'Authorization: Bearer ' + auth_token,
    #     'Content-Type: multipart/form-data;boundary=' + boundary,
    #     'Content-Disposition: form-data; name="mac"' + eol + mac,
    #     'Content-Disposition: form-data; name="' + firmware_file_name_no_ext + '"; filename="' + dumps(firmware_file) + '"',
    #     'Content-Type: application/octet-stream'
    # ]
    #return headers

    fileContent = open(firmware_file, mode='rb').read()
    # return fileContent
    payload_content = base64.b64encode(fileContent)
    return payload_content

@app.route('/reboot-devices')
def reboot_devices(macs):
    url =  '/api/devices?command=reboot'
    return 'rebooting macs'

#enables video server
@app.route('/enable-video-server')
def enable_video_server():
    #TODO define URL
    return 'enabling video server'

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
    http_method = 'POST'
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
def get_modules():
    ip = app.config["IP_ADDRESS"]
    # TODO pull from /api/devices to get correct dimensions and pitch
    return 'pull from /api/devices'
    api_route = "/api/devices"
    response = requests.get('http://' + ip + api_route).json()

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
        #'pitch': pitch_dimensions[module_a['size']['width']],
        'mac': module_a['mac']
    }
    modules[module_b_side] = {
        #'pitch': pitch_dimensions[module_b['size']['width']],
        'mac': module_b['mac']
    }

    return modules



