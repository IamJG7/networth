'''
configuration blueprint module defines configuration API routes
'''

import os
from flask import Blueprint, abort, jsonify, make_response, request

from internal.api_service.routes import logger
from internal.api_service.routes import forwarder

NAME="configuration"
URL_PREFIX=os.path.join("/", "api", "v1", "configure")

configuration_blueprint = Blueprint(name=NAME, import_name=__name__, url_prefix=URL_PREFIX)

@configuration_blueprint.route("watchlist", methods=["GET", "POST"])
def watchlist():
    '''
    watchlist route add and retrieve Stocks & ETFs
    '''
    try:
        if request.method.upper() == "GET":
            user_data = request.args
            result = forwarder.get_watchlist(user_data=user_data)
            return make_response(jsonify({'status_code': 200, 'status': None,
                                      'data': result,
                                      'isShowToaster': True, 'message': None}), 200)
        if request.method.upper() == "POST":
            user_data = request.get_json(force=True)
            status = forwarder.add_watchlist(user_data=user_data.get("user_data"))
            if status == "success":
                return make_response(jsonify({'status_code': 201, 'status': status,
                                        'data': None,
                                        'isShowToaster': True, 'message': 'Successfully updated the watchlist'}), 201)
        abort(405)
    except Exception as err:
        logger.error(f"Failed to perform {request.method} operation for {watchlist.__name__}: {err}")
        abort(500)
