import jwt
from django.http import HttpResponse

from . import settings


def jwt_authentication_middleware(get_response):
    def middleware(request):
        if request.path in settings.UNAUTHENTICATED_PATHS:
            return get_response(request)

        try:
            bearer_header = request.headers['Authorization']
            if not bearer_header.startswith('Bearer'):
                return HttpResponse('Unauthorized', status=401)

            jwt_token = bearer_header[7:]

            private_key = settings.SECRET_KEY
            decoded_jwt = jwt.decode(jwt_token, private_key, algorithms=['HS256'])
            print(decoded_jwt)
            user = decoded_jwt['sub']

            if user:
                request.user = request._cached_user = user
            else:
                return HttpResponse('Unauthorized', status=401)

            return get_response(request)
        except (KeyError, jwt.DecodeError) as e:
            print(e)
            return HttpResponse('Unauthorized', status=401)

    return middleware
