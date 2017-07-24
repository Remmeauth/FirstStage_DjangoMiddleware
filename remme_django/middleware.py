from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import authenticate


class AuthenticationMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured()
        if not request.user.is_authenticated():
            user = authenticate(request=request)
            if user and user.is_authenticated():
                request.user = user
        response = self.get_response(request)
        return response
