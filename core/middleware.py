from django.conf import settings
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.middleware import get_user
from rest_framework.authtoken.models import Token
from re import sub


class CustomAuthenticationClass(AuthenticationMiddleware):

    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The Django users middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE%s setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        ) % ("_CLASSES" if settings.MIDDLEWARE is None else "")
        header_token = request.META.get('HTTP_AUTHORIZATION', None)
        if header_token is not None:
            try:
                token = sub('Token ', '',
                            request.META.get('HTTP_AUTHORIZATION', None))
                token_obj = Token.objects.get(key=token)
                request.user = token_obj.user
            except Token.DoesNotExist:
                request.user = SimpleLazyObject(lambda: get_user(request))
        else:
            request.user = SimpleLazyObject(lambda: get_user(request))
