from flask import Blueprint, current_app, request, jsonify
from cryptography.hazmat.primitives import serialization
from py_vapid import Vapid01 as Vapid
from py_vapid import b64urlencode

from . import models

app = Blueprint('push', __name__)


@app.route('/register', methods=["POST"])
def register():
    current_app.logger.debug(request.json)
    registration = models.PushRegistration.query.filter_by(key=request.json.get('key')).first()
    if registration is not None:
        current_app.logger.debug('Already registered for %s', request.json.get('key'))
        return jsonify({"success": True, "status": "already registered"})
    registration = models.PushRegistration(request.json)
    models.db.session.add(registration)
    models.db.session.commit()
    return jsonify({"success": True})


def init_vapid():
    vapid = Vapid.from_file(current_app.config.get('VAPID_KEY'))
    current_app.config['VAPID_PRIVATE_KEY'] = vapid.private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption())
    application_server_key = vapid.public_key.public_numbers().encode_point()
    current_app.config['VAPID_APPLICATION_SERVER_KEY'] = b64urlencode(application_server_key)
