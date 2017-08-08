from flask import Flask, render_template, abort, request
from sqlalchemy import desc
import os

try:
    from raven.contrib.flask import Sentry
except ImportError:
    Sentry = None

from . import models, api, config, version, socketio

app = Flask(__name__)

app.config.from_object(config.DefaultConfig)
app.config.from_pyfile('orgsms_config.py', silent=True)
app.config.from_envvar('ORGSMS_SETTINGS', silent=True)

if Sentry is not None:
    if "SENTRY_CONFIG" in app.config and "release" not in app.config['SENTRY_CONFIG']:
        app.config['SENTRY_CONFIG'] = version.__version__
    sentry = Sentry(app)

os.makedirs(app.config['MMS_STORAGE'], exist_ok=True)

models.db.init_app(app)
socketio.socketio.init_app(app)

with app.app_context():
    models.db.create_all()

app.register_blueprint(api.app, url_prefix="/api")


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
