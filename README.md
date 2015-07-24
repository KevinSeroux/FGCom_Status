INSTALLATION
============

1. Adjust Asterisk Manager Interface settings (/etc/asterisk/manager.conf):

    ```
    ; User that listen new calls and hangup events, you must change: [fgcom] and secret=fgcom
    [fgcom]
    secret=fgcom
    deny=0.0.0.0/0.0.0.0
    permit = 127.0.0.1/255.255.255.0
    read=call
    write=originate,call
    ```
2. Rename local_settings.py.sample to local_settings.py and write in this file your preference.

3. Install a virtual environment for Python 3 and install dependencies:
    ```bash
    mkvirtualenv --python=/usr/bin/python3 fgcom
    pip install -r requirements.txt
    ```

4. Setup the database:
    ```./manage.py migrate```

5. Fill the database with points and frequencies (Airports, NDB, VOR, LOC, GS and DME)
    ```./manage.py populate```

6. Replace Asterisk's dialplan:
    ```bash
    ./manage.py dialplan > /tmp/fgcom.conf
    sudo mv /tmp/fgcom.conf /etc/asterisk/
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
