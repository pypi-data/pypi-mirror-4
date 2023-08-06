import django.http

__all__ = ["HttpResponseException",
           "BadRequest",
           "NotFound",
           "Forbidden",
           "NotAllowed",
           "Gone",
           "ServerError",
           "UnusualHttpMiddleware"]

class HttpResponseException(Exception):
    def __init__(self, *args, **kwargs):
        super(HttpResponseException, self).__init__(*args)
        self.response = None

class BadRequest(django.http.HttpResponseBadRequest, HttpResponseException):
    pass

class NotFound(django.http.HttpResponseNotFound, HttpResponseException):
    pass

class Forbidden(django.http.HttpResponseForbidden, HttpResponseException):
    pass

class NotAllowed(django.http.HttpResponseNotAllowed, HttpResponseException):
    pass

class Gone(django.http.HttpResponseGone, HttpResponseException):
    pass

class ServerError(django.http.HttpResponseServerError, HttpResponseException):
    pass

class UnusualHttpMiddleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, django.http.HttpResponse):
            return exception
        else:
            return None
