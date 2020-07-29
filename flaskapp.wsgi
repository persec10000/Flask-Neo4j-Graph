#!/usr/bin/python3
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/FlaskApp/")
sys.path.insert(0,"/var/www/FlaskApp/FlaskApp")
sys.path.insert(0,"/home/ubuntu/.local/lib/python3.6/site-packages")



for p in sys.path:
    print(p)

from FlaskApp import app as application
application.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'

