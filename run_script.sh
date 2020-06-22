#!/bin/sh

# Useful for running Python scripts in a production environment.
# (for example, to access models to add users, etc)

if [ "$#" -ne 1 ] || ! [ -e "$1" ]; then
    echo "Usage: $0 PYTHON_SCRIPT" >&2
    exit 1
fi

DJANGO_SETTINGS_MODULE=examreg.settings.production \
  ../env/bin/python3 manage.py shell \
  -c "exec(open('$1').read())"
