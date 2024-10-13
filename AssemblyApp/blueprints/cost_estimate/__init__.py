from flask import Blueprint

cost_estimate_bp = Blueprint('cost_estimate', __name__, template_folder='templates')

from . import routes

