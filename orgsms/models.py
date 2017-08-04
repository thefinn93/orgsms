from flask_sqlalchemy import SQLAlchemy
import datetime

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


class Message(db.Model):
    """Represents an SMS or MMS."""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    local_number = db.Column(db.Integer, db.ForeignKey('phone_number.number'))
    remote_number = db.Column(db.Integer, db.ForeignKey('contact.number'))
    inbound = db.Column(db.Boolean)
    mms = db.Column(db.Boolean)
    text = db.Column(db.String)
    attachment = db.Column(db.String)
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
