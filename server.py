from waitress import serve
from vmck.wsgi import application
import sys

if __name__ == '__main__':
    serve(application, port='8000')
