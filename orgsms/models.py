from flask_sqlalchemy import SQLAlchemy
from flask import current_app
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
        self.filename = os.path.join(current_app.config.get('MMS_STORAGE'), str(uuid.uuid4()))

        if url is not None:
            current_app.logger.debug("Downloading %s to %s", url, self.filename)
            r = requests.get(url, stream=True)
            stream = r.raw

        with open(self.filename, 'wb') as f:
            copyfileobj(stream, f)


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

    def dict(self):
        d = self.__dict__
        if not isinstance(self.timestamp, float):
            d['timestamp'] = self.get_timestamp()
        if '_sa_instance_state' in d:
            del d['_sa_instance_state']
        return d
