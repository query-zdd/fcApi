from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework import request



class Error(Exception):

    def __init__(self, error_code, message=u'服务器异常', request=None, status_code=status.HTTP_400_BAD_REQUEST):
        self.error_code = error_code
        self.message = message
        self.request = request
        self.status_code = status_code

    def __unicode__(self):
        return u'[Error] %d: %s' % (self.err_code, self.message)

    def getResponse(self):
        return ErrorResponse(self.err_code, self.message, self.request)


def ErrorResponse(error_code=500, message=u'服务器异常',request=None):
    request = request.method +" "+ request.get_full_path()
    err = {
        'error_code': error_code,
        'request': request,
        'message': message,
    }
    return Response(err)



def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, Error):
        return ErrorResponse(exc.err_code, exc.err_message, exc.message, status=exc.status_code)
    if response is not None:
        response.data['error_code'] = response.status_code
        response.data['message'] = response.data['detail']
        # response.data['data'] = None #可以存在
        del response.data['detail']  # 删除detail字段
    return response