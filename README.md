## To get started...

requires python3

Clone this repository locally.

Then you can set up the python librarys by installing from the requirements.txt or you can install the requirements manually.

conda install -c anaconda flask
conda install -c anaconda pillow 
conda install -c anaconda matplotlib 
conda install -c carta jwt
pip install uwsgi
pip install bcrypt

setting up opencv is a little difficult. One way to do it is with anaconda. This will avoid having to compile.

conda install -c conda-forge opencv

finally, start the local server with:

FLASK_APP=server.py flask run

Then navigate to the app with your browser.


There is no security set up, so run it locally, not on the open internet.

### Linux install

1. install miniconda and setup an environment

2. Install dependencies:

apt-get install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev poppler-utils build-essential libffi-dev python-dev python-numpy python-matplotlib libgl1-mesa-glx

conda install -c conda-forge opencv
conda install -c anaconda flask pillow matplotlib 
pip install jwt bcrypt

3. Run local server

FLASK_APP=server.py flask run --host=HOSTNAME --port=5000

