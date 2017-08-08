from flask import request, current_app, abort
import requests

from orgsms import models


def receive():
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
        local_number = models.PhoneNumber(number=destination, provider="dummy")
        models.db.session.add(local_number)

    attachment = None
    if mms:
        attachment = models.Attachment(url=text)
        models.db.session.add(attachment)

    message = models.Message(local_number=destination, remote_number=source, attachment=attachment,
                             inbound=True, mms=mms, text=text)
    current_app.logger.info("Receiving from %s to %s message %s", source, destination, text)
    return message


def send(message):
    current_app.logger.info("Sending from %s to %s message %s", message.local_number, message.remote_number,
                            message.text)
    return True
