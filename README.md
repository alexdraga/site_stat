# site_stat deploy

***

### 1. Prepare folders
```
mkdir logs
mkdir uwsgi
mkdir nginx
mkdir supervisor
```

### 2. Prepare packages
```
apt-get update
apt-get install nginx uwsgi git python-pip python-dev supervisor nano virtualenv htop uwsgi-plugin-python
```

### 3. Prepare virtualenv
```
virtualenv site_stat_env
source ./site_stat_env/bin/activate
```

### 4. Prepare source
```
git clone https://github.com/alexdraga/site_stat.git site_stat_app
pip install -r ./site_stat_app/requirements.txt
```

### 5. Prepare django app
```
./manage.py migrate
./manage.py collectstatic
./manage.py createsuperuser
```

### 6. Set django app configs
```
>>site_stat_app/site_stat/settings_local.py
ALLOWED_HOSTS = ['%ip']
DEBUG = False
```

### 7. Setup uwsgi/nginx/supervisor
```
cp /home/root/site_stat_app/deploy/site_stat.ini ./uwsgi
cp /home/root/site_stat_app/deploy/uwsgi_params ./uwsgi
cp /home/root/site_stat_app/deploy/nginx.conf ./nginx
cp /home/root/site_stat_app/deploy/supervisor.conf ./supervisor
```

### 8. Check uwsgi/nginx/supervisor params 
- Check pathes
- Check ip addresses
- Check access rights for nginx to static/files folder

### 9. Link nginx/supervisor/static directories
```
ln -s /home/root/nginx/nginx.conf /etc/nginx/sites-enabled/
ln -s /home/root/supervisor/supervisor.conf  /etc/supervisor/conf.d/
ln -s /home/root/site_stat_app/files/ /home/root/site_stat_app/static
```

### 10. Restart nginx, start supervisor
```
/etc/init.d/nginx restart
/usr/bin/supervisorctl reread
/usr/bin/supervisorctl reload
```
