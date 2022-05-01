from django.core.management.base import BaseCommand, CommandError
from rest_framework.authtoken.models import Token
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

class GetHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        token = self.headers.get('AUTHORIZATION').split(' ')[1]
        try:
            token_found = Token.objects.get(key=token)
            if token_found:
                self.send_response(200)
        except Exception as e:
            self.send_response(403)
        self.send_header('Content-Type',
                         'text/plain; charset=utf-8')
        self.end_headers()

class Command(BaseCommand):

    help = 'Validate token'

    def add_arguments(self, parser):
        parser.add_argument('port', nargs='+', type=int)
        # pass

    def handle(self, *args, **options):
        port = options['port'][0]
        server = HTTPServer(('localhost', port), GetHandler)
        print('Starting server, use <Ctrl-C> to stop')
        server.serve_forever()        

