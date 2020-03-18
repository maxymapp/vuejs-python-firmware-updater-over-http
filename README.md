This is a Flask web app.
We recommend using the latest version of Python 3. Flask supports Python 3.5 and newer, Python 2.7, and PyPy.

How to launch the app?

Checkout this project or simply download the archive (if SSL certificate problem: self signed certificate)
% cd "project-folder" (Navigate to the downloaded folder.)

Activate the environment
Before you work on your project, activate the corresponding environment:
% . venv/bin/activate
Your shell prompt will change to show the name of the activated environment.


% pip install Flask

% export FLASK_ENV=development

[before you run the app, please update config.cfg
    IP_ADDRESS = "10.0.0.3" #device IP
    FIRMWARE_PATH = "/...your....path..../DemoFirmware/"
]

% flask run

