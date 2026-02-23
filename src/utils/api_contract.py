# from src.core.response_code import ResponseCode
class ResponseCode:
    SUCCESS = 0
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    DATABASE_ERROR = 505

class APIContract:
    @staticmethod
    def success(data):
        return {
            "status": "success",
            "code": ResponseCode.SUCCESS,
            "message": "Request was successful",
            "data": data
        }

    @staticmethod
    def error(status_code, message):
        return {
            "status": "error",
            "code": status_code,
            "message": message
        }