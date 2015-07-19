INSTALLATION
============

1. Rename local_settings.py.sample to local_settings.py and write in this file your preference.

2. Install a virtual environment for Python 3 and install dependencies:
    ```python
    mkvirtualenv --python=/usr/bin/python3 fgcom
    pip install -r requirements.txt
    ```

3. Setup the database:
    ```./manage.py migrate
    ```

4. Fill the database with airports, frequencies
    ```./manage.py populate
    ```

EXECUTION
=========

Development
-----------

To launch the AMI Listener:
    ```./ami.py```
    
To launch the web application:
    ```./manage.py runserver```

Production
----------

1. See how to deploy django : https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/

2. Install supervisor and create a file in /etc/supervisor/conf.d/fgcom_ami_listener.conf containing:
   ```
	    [program:fgcom_ami_listener]
            command=/var/www/fgcom/ami.py  # To modify
            environment=PATH="/home/user/Envs/fgcom/bin"  # To modify
            autostart=true
            autorestart=true
            stderr_logfile=/var/log/fgcom_ami_listener.err.log
            stdout_logfile=/var/log/fgcom_ami_listener.out.log
    ```

3. Restart supervisor and check that ami.py is launched.
