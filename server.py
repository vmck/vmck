from waitress import serve
from vmck.wsgi import application

if __name__ == '__main__':
    serve(application, port='8000', threads=28)
