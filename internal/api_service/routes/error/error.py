'''
error blueprint module defines errored API routes
'''

from flask import Blueprint, jsonify, make_response

from internal.api_service.routes import logger

NAME="error"
FAILURE = "failure"

error_blueprint = Blueprint(name=NAME, import_name=__name__)

@error_blueprint.app_errorhandler(405)
def error_405(err):
    '''
    HTTP 405 Error
    '''
    logger.error(err)
    return make_response(jsonify({'status_code': 405, 'status': FAILURE,
                                  'data': None,
                                  'isShowToaster': True, 'message': err.description}), 405)

@error_blueprint.app_errorhandler(500)
def error_500(err):
    '''
    HTTP 500 Error
    '''
    return make_response(jsonify({'status_code': err.description[0], 'status': FAILURE,
                                'data': None,
                                'isShowToaster': True, 'message': err.description[1]}), 500)

@error_blueprint.app_errorhandler(501)
def error_501(err):
    '''
    HTTP 501 Error
    '''
    return make_response(jsonify({'status_code': 501, 'status': FAILURE,
                                'data': None,
                                'isShowToaster': True, 'message': err.description}), 501)