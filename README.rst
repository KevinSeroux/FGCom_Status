INSTALLATION
============

1. Rename local_settings.py.sample to local_settings.py and write in this file your preference.

2. Install a virtual environment for Python 3 and install dependencies:
    mkvirtualenv --python=/usr/bin/python3 fgcom
    pip install -r requirements.txt


EXECUTION
=========

For development, use:
    ./manage.py runserver --noreload
... otherwise, the AMI Listener will be executed twice.

For production, see: https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/