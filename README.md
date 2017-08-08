# site_stat

git clone ...
cd site_stat
virtualenv env
source env/bin/activate

pip install -r requirements.txt

# may be need create db
./manage.py migrate
./manage.py createsuperuser

# set next dependencies
# common
apt-get install nginx uwsgi git memcached python-pip python-setuptools uwsgi-plugin-python python-dev build-essential libpq-dev

# create settings_local.py 
The file should be situated unear settings.py
