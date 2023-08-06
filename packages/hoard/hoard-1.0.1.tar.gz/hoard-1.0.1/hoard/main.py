import argparse

from frontend import FrontEnd


def run():
    f = FrontEnd()

    parser = argparse.ArgumentParser(
        prog='hoard',
        epilog="See '%(prog)s <command> --help' for more help on a specific command."
    )

    sub_parsers = parser.add_subparsers(title='Commands')

    get_parser = sub_parsers.add_parser('get', help='Retrieve variables for a specific deployment')
    get_parser.add_argument('get', action='store_true', help=argparse.SUPPRESS)
    get_parser.add_argument('--project')
    get_parser.add_argument('--env')
    get_parser.set_defaults(func=f.get)

    set_parser = sub_parsers.add_parser('set', help='Create/update variable(s) in a specific deployment.')
    set_parser.add_argument('set', nargs='+', metavar='VAR=value')
    set_parser.add_argument('--project')
    set_parser.add_argument('--env')
    set_parser.set_defaults(func=f.set)

    rm_parser = sub_parsers.add_parser('rm', help='Delete variable(s) in a specific deployment.')
    rm_parser.add_argument('rm', nargs='+', metavar='VAR')
    rm_parser.add_argument('--project')
    rm_parser.add_argument('--env')
    rm_parser.set_defaults(func=f.rm)

    project_parser = sub_parsers.add_parser('project', help='Project specific commands.')
    project_parser.add_argument('project', nargs='?', metavar='PROJECT', default='', help='default to project specified in ~/.hoardrc or .hoard')
    project_parser.add_argument('--add', metavar='PROJECT')
    project_parser.add_argument('-e', '--envs', action='store_true', help='show specified project\'s envs')
    project_parser.add_argument('-l', '--list', action='store_true', help='list all projects')
    project_parser.set_defaults(func=f.project)

    env_parser = sub_parsers.add_parser('env', help='Environment specific commands.')
    env_parser.add_argument('env', action='store_true', help=argparse.SUPPRESS)
    env_parser.add_argument('-a', '--all', action='store_true', help='show all envs')
    env_parser.set_defaults(func=f.env)

    login_parser = sub_parsers.add_parser('login', help='Authenticate with the server backend.')
    login_parser.add_argument('login', action='store_true', help=argparse.SUPPRESS)
    login_parser.set_defaults(func=f.login)

    logout_parser = sub_parsers.add_parser('logout', help='Clear auth details.')
    logout_parser.add_argument('logout', action='store_true', help=argparse.SUPPRESS)
    logout_parser.set_defaults(func=f.logout)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    run()

