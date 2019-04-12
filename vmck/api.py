from django.http import JsonResponse
from django.urls import path


def home(request):
    return JsonResponse({
        'version': '0.0.1',
    })


urls = [
    path('', home),
]
