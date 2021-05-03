from django.http import request
from lin.utils import *
from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code

    return response


class APIException():
    code = 500
    message = '抱歉，服务器未知错误'
    error_code = 999

    def __init__(self, message=None, code=None, error_code=None,
                 headers=None):
        if code:
            self.code = code
        if error_code:
            self.error_code = error_code
        if message:
            self.message = message
        if headers is not None:
            headers_merged = headers.copy()
            headers_merged.update(self.headers)
            self.headers = headers_merged

        super(APIException, self).__init__(message, None)

    def get_body(self, environ=None):
        body = dict(
            message=self.message,
            error_code=self.error_code,
            request=request.method + '  ' + self.get_url_no_param()
        )
        text = json_encode(body)
        return (text)

    @staticmethod
    def get_url_no_param():
        full_path = str(request.full_path)
        main_path = full_path.split('?')
        return main_path[0]

    def get_headers(self, environ=None):
        return [('Content-Type', 'application/json')]


class Success(APIException):
    code = 201
    message = '成功'
    error_code = 0


class DeleteSuccess(APIException):
    code = 211
    message = '删除成功'
    error_code = 0


class Failed(APIException):
    code = 400
    message = '失败'
    error_code = 9999


class AuthFailed(APIException):
    code = 401
    message = '认证失败'
    error_code = 10000


class NotFound(APIException):
    code = 404
    message = '资源不存在'
    error_code = 10020


class ParameterException(APIException):
    code = 400
    message = '参数错误'
    error_code = 10030


class InvalidTokenException(APIException):
    code = 401
    message = '令牌失效'
    error_code = 10040


class ExpiredTokenException(APIException):
    code = 422
    message = '令牌过期'
    error_code = 10050


class UnknownException(APIException):
    code = 500
    message = '服务器未知错误'
    error_code = 999


class RepeatException(APIException):
    code = 400
    message = '字段重复'
    error_code = 10060


class Forbidden(APIException):
    code = 401
    message = '不可操作'
    error_code = 10070


class RefreshException(APIException):
    code = 401
    message = 'refresh token 获取失败'
    error_code = 10100


class FileTooLargeException(APIException):
    code = 413
    message = '文件体积过大'
    error_code = 10110


class FileTooManyException(APIException):
    code = 413
    message = '文件数量过多'
    error_code = 10120


class FileExtensionException(APIException):
    code = 401
    message = '文件扩展名不符合规范'
    error_code = 10130

class OffsetException(APIException):
    code = 413
    message = '偏移量超出范围'
    error_code = 10140

class OnlyException(APIException):
    code = 413
    message = '只能存在一条信息'
    error_code = 10150
