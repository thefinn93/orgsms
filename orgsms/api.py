from flask import Blueprint, abort, jsonify, request, current_app, Response
import datetime
from sqlalchemy import desc

from .provider import providers
from .socketio import socketio
from . import models, exceptions

app = Blueprint('api', __name__)


@app.route('/inbound/<provider>', methods=["POST"])
def inbound(provider):
    if provider in providers:
        message = providers[provider].receive()
        models.db.session.add(message)
        models.db.session.commit()
        socketio.emit('newmessage', message.dict())
        return Response()
    else:
        return abort(404)


def send(local_number, remote_number, text, provider=None):
    if provider is None:
        local = models.PhoneNumber.query.get(local_number)
        if local is not None:
            provider = local.provider
        if provider is None:
            raise exceptions.CantDetermineProviderException()
    if provider not in providers:
        raise exceptions.UnknownProviderException("Provider {} unknown".format(provider))

    message = models.Message(local_number=local_number, remote_number=remote_number,
                             inbound=False, mms=False, text=text)
    models.db.session.add(message)
    current_app.logger.debug("Sending %s to %s from %s", text, remote_number, local_number)
    providers[provider].send(message)
    models.db.session.commit()
    socketio.emit('newmessage', message.dict())
    return message


@app.route('/outbound', methods=["POST"])
def outbound():
    try:
        message = send(request.form.get("from"), request.form.get("to"), request.form.get("text"))
        return jsonify({"id": message.id})
    except (exceptions.CantDetermineProviderException, exceptions.UnknownProviderException):
        return abort(400)


@socketio.on('send')
def outbound_socket(json):
    try:
        message = send(json.get("from"), json.get("to"), json.get("text"))
        return {"success": True, "message": message.dict()}
    except (exceptions.CantDetermineProviderException, exceptions.UnknownProviderException):
        current_app.logger.exception("Failed to send %s", str(json))
        return {"success": False}


@app.route('/messages/<number>')
def get_messages(number):
    results = []
    query = models.Message.query.filter_by(remote_number=number)
    if request.args.get('after') is not None:
        after = datetime.datetime.fromtimestamp(float(request.args.get('after')))
        query = query.filter(models.Message.timestamp > after)
    if request.args.get('before') is not None:
        before = datetime.datetime.fromtimestamp(float(request.args.get('before')))
        query = query.filter(models.Message.timestamp < before)
    query = query.order_by(desc(models.Message.timestamp)).limit(50)
    for message in query.all():
        results.append({
            "mms": message.mms,
            "inbound": message.inbound,
            "text": message.text,
            "attachment": message.attachment,
            "timestamp": message.timestamp.timestamp()
        })
    return jsonify(results)


@app.route("/messages")
def get_conversations():
    query = models.db.session.query(models.Message.remote_number.distinct().label("number"))
    conversations = []
    for conversation in query.all():
        contact = models.Contact.query.filter_by(number=conversation.number).first()
        conversations.append({
            "number": conversation.number,
            "name": contact.name if contact is not None else None
        })
    return jsonify(conversations)
