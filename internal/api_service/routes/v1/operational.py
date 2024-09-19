'''
operational blueprint module defines operational API routes
'''

import os
from flask import Blueprint, abort

NAME="operational"
URL_PREFIX=os.path.join("api", "v1", "operational")

operational_blueprint = Blueprint(name=NAME, import_name=__name__, url_prefix=URL_PREFIX)