import ConfigParser
import getpass
import os
import sys

import requests
from termcolor import colored

from api import API, EnvDoesNotExist, get_token, NoDeploymentVars, ProjectDoesNotExist


BASE_HTTP_ERROR_MESSAGE = 'An error occurred connecting to the server. Is your URL correct?'
CONFIG_SECTION = 'hoard'
GLOBAL = os.path.expanduser('~/.hoardrc')
LOCAL = os.path.join(os.getcwd(), '.hoard')


class FrontEnd(object):
    def config_get(self, key):
        config = ConfigParser.ConfigParser()
        config.read((GLOBAL, LOCAL))  # local will override global

        try:
            value = config.get(CONFIG_SECTION, key)
        except ConfigParser.NoOptionError:
            value = False

        return value

    def config_set(self, key, data):
        config = ConfigParser.ConfigParser()
        config.read(GLOBAL)
        if not config.has_section(CONFIG_SECTION):
            config.add_section(CONFIG_SECTION)
        config.set(CONFIG_SECTION, key, data)
        with open(GLOBAL, 'wb') as config_file:
            config.write(config_file)

    def env(self, args):
        self.preflight()
        if args.env and not args.all:
            env = self.config_get('env')
            if env:
                print(env)
            else:
                print('No env set')

        if args.all:
            try:
                for env in self.api.envs():
                    print(env['name'])
            except requests.HTTPError:
                self.exit_with_error(BASE_HTTP_ERROR_MESSAGE)

    def env_does_not_exist(self, project, env):
        print('"{0}" isn\'t an environment for "{1}", try:'.format(env, project))
        for env in self.api.projects(project)['envs']:
            print('  * {0}'.format(env))
        sys.exit(1)

    def exit_with_error(self, msg, args=()):
        sys.stderr.write(colored(msg.format(*args) + '\n', 'red'))
        sys.exit(1)

    def get(self, args):
        self.preflight()
        project = self.get_var('project', args.project)
        env = self.get_var('env', args.env)

        try:
            pairs = self.api.pairs(project, env)
        except requests.HTTPError:
            self.exit_with_error(BASE_HTTP_ERROR_MESSAGE)
        except NoDeploymentVars:
            msg = '"{0}: {1}" has no environment variables.'
            print(msg.format(project, env))
        except ProjectDoesNotExist:
            self.project_does_not_exist(project)
        except EnvDoesNotExist:
            self.env_does_not_exist(project, env)
        else:
            for pair in pairs.items():
                print('{0}={1}'.format(*pair))

    def get_var(self, var, cli_arg):
        v = cli_arg if cli_arg else self.config_get(var)
        if not v:
            self.exit_with_error('No {0} specified. Use --{0} or set it in your local .hoard'.format(var))
        return v

    def login(self, args=None):
        print('hoard needs to request an access token.')
        print('Your username and password never stored. (Check ~/.hoardrc).\n')
        username = raw_input('Username: ')
        password = getpass.getpass()

        try:
            token = get_token(self.config_get('url'), username, password)
        except requests.HTTPError:
            self.exit_with_error(BASE_HTTP_ERROR_MESSAGE)

        self.config_set('token', token)
        self.api = API(self.config_get('url'), token)

    def logout(self, args):
        config = ConfigParser.ConfigParser()
        config.read(GLOBAL)
        config.remove_option(CONFIG_SECTION, 'token')
        with open(GLOBAL, 'wb') as config_file:
            config.write(config_file)

    def preflight(self):
        if not os.path.exists(GLOBAL):
            self.set_url()
            self.login()

        if os.path.exists(GLOBAL) and self.config_get('url') and self.config_get('token'):
            self.api = API(self.config_get('url'), self.config_get('token'))
            return

        # url is missing
        if not self.config_get('url'):
            self.set_url()

        if not self.config_get('token'):
            self.login()

    def project(self, args):
        self.preflight()
        if args.project and not args.list and not args.envs:
            project = self.config_get('project')
            if not project:
                print('No project set')
                sys.exit()

            print('Deployed with:')
            try:
                for env in self.api.projects(project)['envs']:
                    print('  * {0}'.format(env))
            except requests.HTTPError:
                self.exit_with_error(BASE_HTTP_ERROR_MESSAGE)

        if args.list and not args.envs:
            try:
                for project in self.api.projects():
                    print(project['name'])
            except requests.HTTPError:
                self.exit_with_error(BASE_HTTP_ERROR_MESSAGE)

        if args.envs and not args.list:
            try:
                for env in self.api.projects(args.project)['envs']:
                    print(env)
            except requests.HTTPError:
                self.exit_with_error(BASE_HTTP_ERROR_MESSAGE)

    def project_does_not_exist(self, project):
        msg = '"{0}" doesn\'t exist. To list projects use `hoard project --list`'
        self.exit_with_error(msg.format(project))

    def rm(self, args):
        self.preflight()

        project = self.get_var('project', args.project)
        env = self.get_var('env', args.env)
        try:
            for key in args.rm:
                self.api.rm(project, env, key)
        except ProjectDoesNotExist:
            self.project_does_not_exist(project)
        except EnvDoesNotExist:
            self.env_does_not_exist(project, env)

    def set(self, args):
        self.preflight()
        project = args.project if args.project else self.config_get('project')
        env = args.env if args.env else self.config_get('env')

        pairs = dict({tuple(pair.split('=')) for pair in args.set})

        try:
            self.api.pairs(project, env, pairs)
        except requests.HTTPError:
            self.exit_with_error(BASE_HTTP_ERROR_MESSAGE)
        except ProjectDoesNotExist:
            self.project_does_not_exist(project)
        except EnvDoesNotExist:
            self.env_does_not_exist(project, env)
        else:
            print('Vars set for "{0}: {1}"'.format(project, env))
            for pair in args.set:
                print(pair)

    def set_url(self):
        print("~/.hoardrc doesn't a url. Generating now.")
        url = raw_input('hoard URL: ')
        if not url.startswith(('http://', 'https://')):
            url = 'http://{0}'.format(url)
        self.config_set('url', url)

