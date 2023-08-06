import argparse
import os
import sys

# TODO: quitar esto de aquí!!
sys.path.append('/home/uve/Proyectos/Lemon/LemonFramework')
os.environ['LEMON_CONFIG'] = 'config.Config'

def urls(args):
    from lemon.core.config import LemonConfig
    config = LemonConfig()
    for url in config.urls:
        print(url)

def runserver(args):
    from wsgiref.simple_server import make_server
    from lemon.core.handlers import WSGIHandler
    
    application = WSGIHandler()

    httpd = make_server('', 8888, application)
    httpd.serve_forever()

# Main parser
parser = argparse.ArgumentParser(description='Lemon manage.')
subparsers = parser.add_subparsers(help='sub-command help')

# URLs parser
urls_parser = subparsers.add_parser('urls', help='url help')
urls_parser.set_defaults(func=urls)

# Run server
runserver_parser = subparsers.add_parser('runserver', help='runserver help')
runserver_parser.set_defaults(func=runserver)

# Parse arguments
args = parser.parse_args()
args.func(args)
