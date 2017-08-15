class DefaultConfig(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///orgsms.db'
    VAPID_EMAIL = "orgsms@octothorpe.club"
    VAPID_KEY = "orgsms/vapid.pem"
