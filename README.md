## To get started...

### Mac OS Install

requires python3, opencv and poppler-utils

First, clone this repository locally.

Then you can set up the python libraries by installing from the requirements.txt or you can install the requirements manually.


```
conda install -c anaconda flask pillow matplotlib
conda install -c carta jwt
pip install bcrypt
```

setting up opencv is a little difficult. One way to do it is with anaconda. This will avoid having to compile.


```
conda install -c conda-forge opencv
```

You also need poppler (a pdf utility)

```
brew install poppler 
```

Finally, start the local server with:

```
FLASK_APP=server.py flask run
```

Then navigate to the app with your browser.


There is no security set up, so run it locally, not on the open internet.

### Linux install

First, install miniconda and setup an environment

Next, install dependencies:

```
apt-get install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev poppler-utils build-essential libffi-dev python-dev python-numpy python-matplotlib libgl1-mesa-glx
```

```
conda install -c conda-forge opencv
conda install -c anaconda flask pillow matplotlib 
pip install jwt bcrypt
```

Finally, Run local server

```
FLASK_APP=server.py flask run --host=HOSTNAME --port=5000
```

## Setup

cd into the directory. Run the add_user script to set up a user.
```
python ./add_user.py
```

