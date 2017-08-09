# site_stat

git clone ...
cd site_stat
virtualenv env
source env/bin/activate

pip install -r requirements.txt

# set next dependencies
# common
apt-get install nginx uwsgi git memcached python-pip python-setuptools uwsgi-plugin-python python-dev build-essential libpq-dev

# prepare django app
./manage.py migrate
./manage.py createsuperuser
./manage.py collectstatic
Add settings_local.py with ALLOWED_HOSTS, DEBUG, KEY?
The file should be situated near settings.py

# set /home/root/uwsgi/uwsgi.ini
[uwsgi]
chdir = /home/root/site_stat/
module = site_stat.wsgi:application
processes = 1
threads = 1
master = true
socket = 127.0.0.1:8001
master = true

# set /home/root/nginx/nginx.conf
# site_stat.conf

# the upstream component nginx needs to connect to
upstream django {
    server 127.0.0.1:8001; # for a file socket
}

# configuration of the server
server {
    # the port your site will be served on
    listen      80;
    # the domain name it will serve for
    server_name x.x.x.x; # substitute your machine's IP address or FQDN
    charset     utf-8;

    # max upload size
    client_max_body_size 75M;   # adjust to taste

    location /static {
        alias /home/root/site_stat/static; # your Django project's static files - amend as required
    }

    # Finally, send all non-media requests to the Django server.
    location / {
        uwsgi_pass  django;
        include     /home/root/uwsgi/uwsgi_params; # the uwsgi_params file you installed
    }
}

# set uwsgi_params from https://github.com/nginx/nginx/blob/master/conf/uwsgi_params

# link nginx.conf and restart nginx, start uwsgi
ln -s /home/root/nginx/site.conf /etc/nginx/sites-enabled/
uwsgi --ini ./uwsgi/site_stat.ini &
/etc/init.d/nginx restart

# link /files path to /static 
ln -s /home/draga/site_stat/files/ /home/draga/site_stat/static

# setup supervisor
apt-get install supervisor
link conf file:
ln -s /home/root/supervisor/supervisord.conf  /etc/supervisor/conf.d/
conf file as follows:


[program:uwsgi]
command=uwsgi --ini ./uwsgi/site_stat.ini
autostart=true
autorestart=true
stderr_logfile = /home/draga/logs/uwsgi_err.log
stdout_logfile = /home/draga/logs/uwsgi_out.log

[program:grab]
directory=/home/draga/site_stat
command=/home/draga/site_stat/manage.py grab
autostart=true
autorestart=true
stderr_logfile = /home/draga/logs/grab_err.log
stdout_logfile = /home/draga/logs/grab_out.log

[program:zip]
directory=/home/draga/site_stat
command=/home/draga/site_stat/manage.py zip
autostart=true
autorestart=true
stderr_logfile = /home/draga/logs/zip_err.log
stdout_logfile = /home/draga/logs/zip_out.log

[program:report]
directory=/home/draga/site_stat
command=/home/draga/site_stat/manage.py report
autostart=true
autorestart=true
stderr_logfile = /home/draga/logs/report_err.log
stdout_logfile = /home/draga/logs/report_out.log

