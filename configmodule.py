class Config(object):
    DEBUG = False
    TESTING = False

class ProductionConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:password@localhost:3306/test'
    SECRET_KEY = 'Jasons Secret'
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:password@localhost:3306/test'
    SECRET_KEY = 'Jasons Secret'
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,

class TestingConfig(Config):
    TESTING = True

class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite://:memory:'
