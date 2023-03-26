sudo apt-get -y install nginx

sudo ufw allow 'Nginx HTTP'
sudo ufw allow ssh
sudo ufw enable

sudo apt-get -y install  libsm6 libxext6 libxrender-dev 
sudo apt-get -y install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
sudo apt-get -y install  python3-venv

cd /home/ubuntu  # go home
mkdir /home/ubuntu/quizgrader; cd /home/ubuntu/quizgrader
python3.6 -m venv quizgrader_venv
sh ~/quizgrader/quizgrader_venv/bin/activate

git clone https://robmacman@bitbucket.org/robmacman/quizgrader.git

cd /home/ubuntu/quizgrader/quizgrader
pip install wheel
pip install -r requirements_linux.txt


# sudo apt-get -y install libpcre3 libpcre3-dev
pip install uwsgi

# copy model data
# scp -i ~/.ssh/LightsailDefaultKey-us-east-1.pem ./ml_data/clf_model-2.joblib  
