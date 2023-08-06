from flask import Flask
from flask.templating import render_template
from flask.ext.marcos.core.manager import InitModule
from config import config
from flask.ext.marcos import Marcos

app = Flask(__name__)
app.config.from_object(config)
marcos = Marcos(app)
db = marcos.db

from modules.users.models import User, Role
InitModule(User, marcos.api_manager)
InitModule(Role, marcos.api_manager)

@app.route('/')
def index():
    return render_template('index.html')

