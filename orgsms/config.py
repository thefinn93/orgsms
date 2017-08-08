class DefaultConfig(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///orgsms.db'
    MMS_STORAGE = "mms-files"
