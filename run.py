#!/usr/bin/env python
from orgsms.socketio import socketio
from orgsms.orgsms import app

socketio.run(app=app, debug=True, host="0.0.0.0")
