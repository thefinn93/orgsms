from flask import Flask, render_template, abort, request
from sqlalchemy import desc
import os

try:
    from raven.contrib.flask import Sentry
except ImportError:
    Sentry = None

from . import models, api, config, version, socketio, push

app = Flask(__name__)

app.config.from_object(config.DefaultConfig)
app.config.from_pyfile('orgsms_config.py', silent=True)
app.config.from_envvar('ORGSMS_SETTINGS', silent=True)

if "SENTRY_DSN" in app.config:
    if Sentry is None:
        app.logger.warning("SENTRY_DSN specified but raven not installed! Please pip install raven[flask]")
    else:
        Sentry(app, dsn=app.config.get('SENTRY_DSN'))

app.config['MMS_STORAGE'] = os.path.join(app.static_folder, "mms-files")
os.makedirs(app.config['MMS_STORAGE'], exist_ok=True)

models.db.init_app(app)
socketio.socketio.init_app(app)

with app.app_context():
    push.init_vapid()
    models.db.create_all()

app.register_blueprint(api.app, url_prefix="/api")
app.register_blueprint(push.app, url_prefix="/push")


@app.before_request
def check_remote_user():
    if "USER_HEADER" in app.config and not request.path.startswith("/api/inbound"):
        if request.headers.get(app.config['USER_HEADER'], "") == "":
            abort(401)


@app.context_processor
def inject_version():
    return dict(orgsms_version=version.__version__)


@app.route('/')
def conversations():
    query = models.Message.query.group_by(models.Message.remote_number).order_by(desc(models.Message.timestamp)).all()
    return render_template('conversations.html', threads=query)


@app.route('/thread/<number>')
def thread(number):
    messages = models.Message.query.filter_by(remote_number=number).all()
    contact = models.Contact.query.filter_by(number=number).first()
    number = models.PhoneNumber.query.first()
    if len(messages) == 0 and contact is None:
        return abort(404)
    return render_template('thread.html', thread=messages, contact=contact, number=number.number)


@app.route('/serviceworker.js')
def serviceworker():
    return app.send_static_file('js/serviceworker.js')
