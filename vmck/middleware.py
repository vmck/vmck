import jwt

from django.http import JsonResponse

from vmck import settings


def jwt_authentication_middleware(get_response):
    def middleware(request):
        if request.path in settings.UNAUTHENTICATED_PATHS or settings.DEBUG:
            return get_response(request)

        try:
            auth_header = request.headers['Authorization']
            if not auth_header.startswith('Bearer'):
                return JsonResponse({'error': 'Unauthorized'})

            jwt_token = auth_header[7:]

            decoded_jwt = jwt.decode(jwt_token,
                                     settings.SECRET_KEY,
                                     algorithms=['HS256'])

            user = decoded_jwt['sub']

            if user:
                # TODO get user object and set it on request
                request.user = request._cached_user = user
            else:
                return JsonResponse({'error': 'Unauthorized'})

            return get_response(request)
        except (KeyError, jwt.DecodeError):
            return JsonResponse({'error': 'Unauthorized'})

    return middleware
