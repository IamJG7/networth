'''
operational blueprint module defines operational API routes
'''

import os
from flask import Blueprint, abort, jsonify, make_response, redirect, request

from internal.api_service.routes import logger
from internal.api_service.routes import forwarder

NAME="operational"
URL_PREFIX=os.path.join("/", "api", "v1", "operational")

SUCCESS = "success"

operational_blueprint = Blueprint(name=NAME, import_name=__name__, url_prefix=URL_PREFIX)

@operational_blueprint.route("transactions/<transaction_id>", methods=["GET"])
def get_transaction(transaction_id):
    '''
    get_transaction
    '''
    try:
        if request.method.upper() == "GET":
            status = forwarder.get_transaction(transaction_id=transaction_id)
            return make_response(jsonify({'status_code': 200, 'status': SUCCESS,
                                      'data': status,
                                      'isShowToaster': True, 'message': None}), 200)
        else:
            abort(405)
    except Exception as err:
        logger.error(f"Failed to perform {request.method} operation for {get_transaction.__name__}: {err}")
        abort(500, description=err.args[0])