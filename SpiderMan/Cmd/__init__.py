"""Usage:
    SpiderMan init
    SpiderMan runserver <host:port>
    SpiderMan admin
    
Options:
    -h --help
    -v --version
"""
from docopt import docopt
from SpiderMan import version
from SpiderMan.Cmd.migrate import create_database, create_admin
from SpiderMan.server.web.main import main as tornado_main


def main():
    arguments = docopt(__doc__, version=version())
    if arguments.get('init'):
        create_database()
        tornado_main()
    elif arguments.get('admin'):
        create_admin()
    elif arguments.get('runserver'):
        tornado_main(dom=arguments.get('<host:port>'))


if __name__ == "__main__":
    main()
