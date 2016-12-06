#! /usr/bin/env python
from app import app
app.run(host='0.0.0.0', port=1024, debug = True, threaded=False) 

#Note about the using threaded option, not for production
#http://stackoverflow.com/questions/14814201/can-i-serve-multiple-clients-using-just-flask-app-run-as-standalone
