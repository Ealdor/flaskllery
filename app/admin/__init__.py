from flask import Blueprint

blueprint = Blueprint('admin', __name__)

from . import views
