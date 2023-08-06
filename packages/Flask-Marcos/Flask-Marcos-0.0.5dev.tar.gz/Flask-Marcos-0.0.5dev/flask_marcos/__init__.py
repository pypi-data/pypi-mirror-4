from flask.ext.mail import Mail
from flask.ext.restless import APIManager
from flask.ext.sqlalchemy import SQLAlchemy

class Marcos(object):

    def __init__(self, app=None):
        self.app = app
        self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.__init_extension()

    def __init_extension(self):
        self.db = SQLAlchemy(self.app)
        self.mail = Mail(self.app)
        self.api_manager = APIManager(self.app, flask_sqlalchemy_db=self.db)
        self.db.create_all()