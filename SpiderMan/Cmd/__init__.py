"""Usage:
    SpiderMan init
    SpiderMan runserver <host:port>
    SpiderMan admin
    
Options:
    -h --help
    -v --version
"""
from docopt import docopt
from tornado.log import app_log
from SpiderMan import version
from SpiderMan.Cmd.migrate import create_database, create_admin
from SpiderMan.server.web.main import main as tornado_main


def main():
    arguments = docopt(__doc__, version=version())
    if arguments.get('init'):
        create_database()
        print("SpiderMan initialization completion,"
              " you can run; SpiderMan runserver "
              "[host:port] to open the service")
    elif arguments.get('admin'):
        create_admin()
    elif arguments.get('runserver'):
        tornado_main(dom=arguments.get('<host:port>'))


if __name__ == "__main__":
    # main()
    tornado_main(dom='127.0.0.1:8080')
