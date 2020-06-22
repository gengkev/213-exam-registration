#!/bin/bash
git pull
chgrp -R www-data *
chmod g+w *

source ../env/bin/activate
export DJANGO_SETTINGS_MODULE=examreg.settings.production
pip install -r requirements.txt --upgrade -q
python manage.py check --deploy
python manage.py collectstatic --no-input
python manage.py migrate
#python manage.py test
deactivate

touch examreg/wsgi.py
