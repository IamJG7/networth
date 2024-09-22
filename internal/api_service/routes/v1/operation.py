'''
operations blueprint module defines operations API routes
'''

import os
from flask import Blueprint, abort, jsonify, make_response, request

from internal.api_service.routes import logger
from internal.api_service.routes import forwarder

NAME="operation"
URL_PREFIX=os.path.join("/", "api", "v1", "operation")

SUCCESS = "success"
FAILURE = "failure"

operation_blueprint = Blueprint(name=NAME, import_name=__name__, url_prefix=URL_PREFIX)

@operation_blueprint.route("generate_password", methods=["POST"])
def generate_password():
    '''
    generate_password route generates alphanumeric passphrase
    '''
    try:
        if request.method.upper() == "POST":
            user_data = request.get_json(force=True)
            passphrase = forwarder.generate_password(user_data=user_data.get("user_data"))
            return make_response(jsonify({'status_code': 200, 'status': SUCCESS,
                                      'data': passphrase,
                                      'isShowToaster': True, 'message': 'Passphrase successfully generated'}), 200)
        else:
            abort(405)
    except Exception as err:
        logger.error(f"Failed to perform {request.method} operation for {generate_password.__name__}: {err}")
        abort(500, description=err.args[0])

@operation_blueprint.route("statistics", methods=["GET", "POST"])
def statistics():
    '''
    statistics route add and retrieve Stock & ETF statistical data
    '''
    try:
        if request.method.upper() == "GET":
            user_data = request.args
            result = forwarder.get_statistics(user_data=user_data)
            return make_response(jsonify({'status_code': 200,
                                          'status': SUCCESS,
                                          'data': result,
                                          'isShowToaster': True,
                                          'message': None}), 200)
        if request.method.upper() == "POST":
            user_data = request.get_json(force=True)
            status = forwarder.add_statistic(user_data=user_data.get("user_data"))
            if status == SUCCESS:
                return make_response(jsonify({'status_code': 201,
                                              'status': status,
                                              'data': None,
                                              'isShowToaster': True,
                                              'message': 'Successfully created a transactionID'}), 201)
        abort(405)
    except Exception as err:
        logger.error(f"Failed to perform {request.method} operation for {statistics.__name__}: {err}")
        abort(500, description=err.args[0])