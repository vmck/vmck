import jwt
from django.http import HttpResponse

from . import settings


def jwt_authentication_middleware(get_response):
    def middleware(request):
        if request.path in settings.UNAUTHENTICATED_PATHS:
            return get_response(request)

        try:
            auth_header = request.headers['Authorization']
            if not auth_header.startswith('Bearer'):
                return HttpResponse('Unauthorized', status=401)

            jwt_token = auth_header[7:]

            private_key = settings.SECRET_KEY
            decoded_jwt = jwt.decode(jwt_token, private_key, algorithms=['HS256'])
            user = decoded_jwt['sub']

            if user:
                # TODO get user object and set it on request
                request.user = request._cached_user = user
            else:
                return HttpResponse('Unauthorized', status=401)

            return get_response(request)
        except (KeyError, jwt.DecodeError):
            return HttpResponse('Unauthorized', status=401)

    return middleware
