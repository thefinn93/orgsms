from flask import Blueprint, current_app, request, jsonify

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
