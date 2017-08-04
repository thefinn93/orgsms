from flask import request, current_app, abort
import requests

from orgsms import models


def receive():
    if "TELI_INBOUND_TOKEN" in current_app.config:
        if request.args.get("token") != current_app.config["TELI_INBOUND_TOKEN"]:
            return abort(401)
    else:
        current_app.logger.warning("No Teli inbound token set! Please set config option TELI_INBOUND_TOKEN")
    current_app.logger.debug(request.form)

    source = request.form.get('source')
    destination = request.form.get('destination')
    text = request.form.get('message')
    mms = request.form.get('type', 'sms') == "mms"

    remote_number = models.Contact.query.filter_by(number=source).first()
    if remote_number is None:
        current_app.logger.info("Adding new contact %s", source)
        remote_number = models.Contact(number=source)
        models.db.session.add(remote_number)

    local_number = models.PhoneNumber.query.get(destination)
    if local_number is None:
        current_app.logger.info("Adding new local phone number %s", destination)
        local_number = models.PhoneNumber(number=destination, provider="teli")
        models.db.session.add(local_number)

    message = models.Message(local_number=destination, remote_number=source, inbound=True, mms=mms, text=text)
    return message


def send(message):
    response = requests.get("https://sms.teleapi.net/sms/send", params={
        "token": current_app.config.get("TELI_OUTBOUND_TOKEN"),
        "source": message.local_number,
        "destination": message.remote_number,
        "message": message.text
    })
    if response.ok:
        parsed = response.json()
        message.provider_id = parsed.get('data')
        message.status = "Delivered to provider"
    return response.ok
