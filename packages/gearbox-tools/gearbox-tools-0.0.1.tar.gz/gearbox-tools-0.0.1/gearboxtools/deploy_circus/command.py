from logging import getLogger
import os, sys

from gearbox.command import Command
from string import Template
from contextlib import closing

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

log = getLogger('gearbox')

class CircusDeployCommand(Command):
    TEMPLATE = Template('''
[env:$app_name]
PATH=$virtual_env/bin:$$PATH
VIRTUAL_ENV=$virtual_env

[watcher:$app_name]
working_dir = $appdir
cmd = chaussette --backend $backend --fd $$(circus.sockets.$app_name) paste:$config_file
use_sockets = True
warmup_delay = 0
numprocesses = 1

stderr_stream.class = FileStream
stderr_stream.filename = $logging_dir/$app_name.log
stderr_stream.refresh_time = 0.3

stdout_stream.class = FileStream
stdout_stream.filename = $logging_dir/$app_name.log
stdout_stream.refresh_time = 0.3

[socket:$app_name]
host = localhost
port = $port
''')

    def get_description(self):
        return 'Generates configuration for deploying a PasteDeploy application on Mozilla Circus'

    def get_parser(self, prog_name):
        parser = super(CircusDeployCommand, self).get_parser(prog_name)

        parser.add_argument("-c", "--config",
            help='application config file to use (default: production.ini)',
            dest='config_file', default="production.ini")

        parser.add_argument("-k", "--skeleton",
            help='template config file to use to generate application configuration file if not found',
            dest='skeleton_file', default="development.ini")

        parser.add_argument("-f", "--force", action='store_true',
            help='If the configuration file exists, replace it anyway with the skeleton',
            dest='force', default=False)

        parser.add_argument("-e", "--environment",
            help='Virtual environment to use for the application, by default the active one',
            dest='virtual_env', default=None)

        parser.add_argument("-d", "--app-dir",
            help='Application working path, by default the current path',
            dest='appdir', default=None)

        parser.add_argument("-a", "--app-name",
            help='Application name, used to create circus configuration sections, '
                 'by default took from PasteDeploy app:main section',
            dest='app_name', default=None)

        parser.add_argument("-p", "--port",
            help='Application port to use, by default took from PasteDeploy server:main section',
            dest='port', default=None)

        parser.add_argument("-l", "--logging-dir",
            help='Directory where to store logging files by default',
            dest='logging_dir', default='/var/log/circus')

        parser.add_argument("-b", "--backend",
            help='Chaussette backend used to serve requests',
            dest='backend', default='waitress')

        parser.add_argument('configuration_options', nargs='*',
            help='When configuration file is not available, the provided options in the form key=value '
                 'will be replaced in the skeleton file to generate one')

        return parser

    def _parse_opts(self, options):
        result = {}
        for arg in options:
            if '=' not in arg:
                raise ValueError('Variable assignment %r invalid (no "=")' % arg)
            name, value = arg.split('=', 1)
            result[name] = value
        return result


    def _make_conf(self, skeleton, config_file, options):
        log.warn('Configuration file not found, generating one from skeleton...')
        skeleton_config = ConfigParser()
        skeleton_config.read(skeleton)

        for name, value in options.items():
            section, name = 'DEFAULT', name
            if '@' in name:
                section, name = name.split('@', 1)
            skeleton_config.set(section, name, value)

        if skeleton_config.sections():
            with closing(open(config_file, 'w')) as config_file:
                skeleton_config.write(config_file)

    def _get_app_and_port(self, config_file):
        conf = ConfigParser()
        conf.read(config_file)

        app_name = conf.get('app:main', 'use')
        server_port = conf.get('server:main', 'port')

        if app_name.startswith('egg:'):
            app_name = app_name[4:]

        return app_name, server_port

    def take_action(self, opts):
        if not opts.virtual_env:
            opts.virtual_env = os.environ.get('VIRTUAL_ENV')

        if not opts.virtual_env:
            log.error('No virtual environment specified and none active')
            return

        if not os.path.exists(opts.config_file) or opts.force:
            self._make_conf(opts.skeleton_file, opts.config_file,
                            self._parse_opts(opts.configuration_options))

        log.info('Using Environment: %s', opts.virtual_env)

        if not opts.appdir:
            opts.appdir = os.getcwd()

        log.info('Using Application Directory: %s', opts.appdir)

        app_name, port = self._get_app_and_port(opts.config_file)

        if not opts.app_name:
            opts.app_name = app_name

        log.info('Using Application Name: %s', opts.app_name)

        if not opts.port:
            opts.port = port

        log.info('Using Port: %s', opts.port)

        print(self.TEMPLATE.substitute(vars(opts)))