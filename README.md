# site_statistic

git clone ...
cd site_stat
virtualenv env
source env/bin/activate

pip install -r requirements.pip

# may be need create db
./manage.py migrate
./manage.py createsuperuser