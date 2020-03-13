import cgi, requests, os, pycurl, array, uuid, re
from urllib.parse import urlencode, quote_plus
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
        return dumps(update_firmware(modules['left']['mac'], left_pitch))
    if right_pitch != str(modules['right']['pitch']):
        return 'right pitch requires update'
        return update_firmware(modules['right']['mac'], right_pitch)
    return 'program finished'

#@app.route('/firm')
def update_firmware(mac, pitch):

    ip  = app.config["IP_ADDRESS"]
    url = 'http://' + ip + '/api/devices?command=update-firmware'
    auth_token = app.config["AUTH_TOKEN"]

    firmware_path = app.config["FIRMWARE_PATH"]
    #return (firmware_path)
    firmware_file_name = app.config["FIRMWARE_FILES"][pitch]
    #return (firmware_file_name)
    firmware_file = firmware_path + firmware_file_name
    #return (firmware_file)

    firmware_file_name_no_ext = re.sub('\.d3$', '', firmware_file_name)
    #return firmware_file_name_no_ext

    # post_data = {
    #     'mac': mac,
    #     'name': firmware_file_name_no_ext,
    #     'filename': firmware_file
    # }
    # postfields = urlencode(post_data)

    boundary = "--" + str(uuid.uuid1().int)
    eol = "\r\n"
    with open(firmware_file, mode='rb') as file:  # b is important -> binary
        fileContent = file.read()

    headers = [
        'Authorization: Bearer ' + auth_token,
        'Content-Type: multipart/form-data;boundary=' + boundary,
        'Content-Disposition: form-data; name="mac"' + eol + mac,
        'Content-Disposition: form-data; name="' + firmware_file_name_no_ext + '"; filename="' + dumps(firmware_file) + '"',
        'Content-Type: application/octet-stream',
        fileContent
    ]
    return headers

    curl = pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(pycurl.HTTPHEADER, headers)
    #curl.setopt(pycurl.POSTFIELDS, postfields)
    #curl.setopt(pycurl.CUSTOMREQUEST, 'POST')

    curl.perform()
    curl.close()

    # curl.setopt(curl.HTTPPOST, [
    #     ('fileupload', (
    #
    #         # Upload the contents of the file
    #         curl.FORM_FILE, '/Users/mkulikovskiy/Documents/DemoFirmware/TCO4_0_60Hz_Internal.d3',
    #         # Specify a file name of your choice
    #         curl.FORM_FILENAME, 'TCO4_0_60Hz_Internal.d3',
    #         # Specify a different content type of upload
    #         curl.FORM_CONTENTTYPE, 'application/octet-stream',
    #     )),
    # ])

    return

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





