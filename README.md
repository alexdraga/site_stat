# site_statistic

git clone ...
cd site_stat
virtualenv env
source env/bin/activate

pip install -r requirements.pip

# may be need create db
./manage.py migrate
./manage.py createsuperuser

# set next dependencies
# common
apt-get install nginx uwsgi git rabbitmq-server postgresql-9.4 memcached python-pip python-setuptools uwsgi-plugin-python nodejs python-dev build-essential libpq-dev
# python-ldap dependencies
apt-get install libldap2-dev libsasl2-dev

# create db and project user