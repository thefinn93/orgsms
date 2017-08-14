from flask_sqlalchemy import SQLAlchemy
from flask import current_app, url_for
import pywebpush
import json
import copy
import datetime
import os
import uuid
import requests
from shutil import copyfileobj

db = SQLAlchemy()


class PhoneNumber(db.Model):
    """Represents a phone number that we control."""
    number = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String)
    provider = db.Column(db.String)


class Contact(db.Model):
    """Represents an external user/number."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    number = db.Column(db.Integer, unique=True)  # TODO: Eventually we should support multiple numbers per contact


class Attachment(db.Model):
    """An attachment to an MMS."""
    __tablename__ = "attachment"
    id = db.Column(db.Integer, primary_key=True)
    filename_original = db.Column(db.String)
    filename = db.Column(db.String)
    message = db.relationship("Message", uselist=False, back_populates="attachment")

    def __init__(self, url=None, stream=None):
        assert url is not None or stream is not None
        self.filename = str(uuid.uuid4())
        path = os.path.join(current_app.config.get('MMS_STORAGE'), self.filename)

        if url is not None:
            current_app.logger.debug("Downloading %s to %s", url, path)
            r = requests.get(url, stream=True)
            stream = r.raw

        with open(path, 'wb') as f:
            copyfileobj(stream, f)

    @property
    def static_path(self):
        return url_for('static', filename="mms-files/{}".format(self.filename))

    def json(self):
        """Returns a JSONifable dictionary."""
        d = self.__dict__
        d['static_path'] = self.static_path
        if '_sa_instance_state' in d:
            del d['_sa_instance_state']
        return d


class Message(db.Model):
    """Represents an SMS or MMS."""
    __tablename__ = "message"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    local_number = db.Column(db.Integer, db.ForeignKey('phone_number.number'))
    remote_number = db.Column(db.Integer, db.ForeignKey('contact.number'))
    inbound = db.Column(db.Boolean)
    mms = db.Column(db.Boolean)
    attachment_id = db.Column(db.Integer, db.ForeignKey('attachment.id'))
    attachment = db.relationship('Attachment', back_populates='message')
    text = db.Column(db.String)
    unread = db.Column(db.Boolean, default=False)
    provider_id = db.Column(db.String)
    status = db.Column(db.String)

    def get_timestamp(self):
        return self.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()

    def json(self):
        d = self.__dict__
        if 'attachment' in d and isinstance(d['attachment'], Attachment):
            d['attachment'] = d['attachment'].json()
        if 'timestamp' in d and not isinstance(d['timestamp'], float):
            d['timestamp'] = self.get_timestamp()
        if '_sa_instance_state' in d:
            del d['_sa_instance_state']
        # import pdb; pdb.set_trace()
        if 'remote_number' in d:
            d['url'] = url_for('thread', number=d['remote_number'])
        return d

    def push(self):
        if not self.inbound:
            return None
        message_json = {"event": "newmessage", "message": copy.deepcopy(self.json())}
        current_app.logger.debug(message_json)
        for registration in PushRegistration.query.all():
            try:
                registration.push(message_json)
            except pywebpush.WebPushException as e:
                registration.record_failure()
        current_app.logger.debug(message_json)


class PushRegistration(db.Model):
    """A push notification subscription."""

    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String)
    key = db.Column(db.String, unique=True)
    auth = db.Column(db.String)
    failures = db.Column(db.Integer, default=0)

    def __init__(self, registration):
        self.endpoint = registration['endpoint']
        self.key = registration['key']
        self.auth = registration['auth']

    @property
    def subscription_info(self):
        return {"endpoint": self.endpoint, "keys": {"auth": self.auth, "p256dh": self.key}}

    def push(self, data):
        pywebpush.webpush(self.subscription_info, data=json.dumps(data))
        self.failures = 0

    def record_failure(self):
        self.failures += 1
        if self.failures > 10:
            current_app.logger.info("Pushing to %s failed 10 times in a row, deleting subscription", self.endpoint)
            db.session.delete(self)
        else:
            current_app.logger.debug("Pushing to %s failed %s times in a row, not deleting yet",
                                     self.endpoint, self.failures)
            db.session.commit()
