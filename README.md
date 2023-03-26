## To get started...

### Mac OS Install

requires python3, opencv and poppler-utils

First, clone this repository locally.

Then you can set up the python libraries by installing from the requirements.txt or you can install the requirements manually.


```
conda install -c anaconda flask pillow matplotlib
conda install -c carta jwt
pip install bcrypt img2pdf
```

setting up opencv is a little difficult. One way to do it is with anaconda. This will avoid having to compile.


```
conda install -c conda-forge opencv
```

You also need poppler (a pdf utility)

```
brew install poppler 
```

You may also need tesseract langauges

```
brew install tesseract-lang 
```

You also need to train your models with the version of sklearn that you install. And if you update the version of sklearn that you use, you will need to update or retrain your models.
You can train the models with this command. But first, make sure your train data is set up.

```
python ./scripts/cv/helpers_for_training.py
```

This will put a model file into the output directory. You can move it where you want, then edit config.py to point to your new model.

You can grade a quiz from a pdf on the command line
```
python -m scripts.cv.main rmcc 111--course-name--test-name create_quiz 111--course-name--test-name.pdf 
```

Finally, start the local server with:

```
FLASK_APP=server.py flask run

or

gunicorn --bind 0.0.0.0:8080 wsgi:application -w 1
```

Then navigate to the app with your browser.


There is no security set up, so run it locally, not on the open internet.

### Linux install

First, install miniconda and setup an environment

Next, install dependencies:

```
sudo apt -y update
sudo apt -y nginx
sudo apt -y install python3-pip python3-venv
sudo apt-get -y install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev poppler-utils build-essential libffi-dev python-dev python-numpy python-matplotlib libgl1-mesa-glx
```

Prepare python environment
```
python3 -m venv venv 
. ./venv/bin/activate
pip install opencv-contrib-python 
pip install gunicorn flask Pillow matplotlib Python-fontconfig pyjwt bcrypt img2pdf flask-login Flask-WTF
```

Finally, Run local server

```
FLASK_APP=server.py flask run --host=0.0.0.0 --port=5000

or

gunicorn --bind 0.0.0.0:8080 wsgi:application -w 1
```

## Setup

cd into the directory. Run the add_user script to set up a user.
```
python ./add_user.py
```

