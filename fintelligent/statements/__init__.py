from flask import Blueprint

statements = Blueprint('statements', __name__)

from . import routes
