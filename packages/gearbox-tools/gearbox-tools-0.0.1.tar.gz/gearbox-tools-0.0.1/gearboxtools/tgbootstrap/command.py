from logging import getLogger

log = getLogger('gearbox')

import shutil, os, contextlib
from gearbox.command import TemplateCommand

BOOTSTRAP = '''  <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/bootstrap/stylesheets/bootstrap.scss')}" />\n'''
BOOTSTRAP_RESPONSIVE = '''  <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/bootstrap/stylesheets/bootstrap-responsive.scss')}" />\n'''
APPEND_PATH = '''
def append_boostrap_include_path(app):
    import tg, os

    include_path = tg.config.get('tgext.scss.include_paths')
    if include_path:
        if isinstance(include_path, str):
            include_path.split(',')
    else:
        include_path = tg.config['tgext.scss.include_paths'] = []

    basepath = os.path.normcase(os.path.abspath((tg.config['paths']['static_files'])))
    include_path.append(basepath + '%(include_path)s')

    return app
base_config.register_hook('before_config', append_boostrap_include_path)
'''

class TGBootstrapCommand(TemplateCommand):
    def get_description(self):
        return 'Adds SCSS based bootstrap to a TurboGears2 project through tgext.scss'

    def get_parser(self, prog_name):
        parser = super(TGBootstrapCommand, self).get_parser(prog_name)
        return parser

    def _find_public(self):
        for d in os.listdir('.'):
            candidate_dir = os.path.join(d, 'public')
            if os.path.exists(candidate_dir):
                return d, candidate_dir

        log.error('Unable to locate public files directory')
        raise RuntimeError('public path not found')

    def _find_master_templates(self, project_dir):
        master_templates = []

        templates_path = os.path.join(project_dir, 'templates')
        for f in os.listdir(templates_path):
            if f.startswith('master.'):
                master_templates.append(os.path.join(templates_path, f))

        return master_templates

    def _find_app_config(self, project_dir):
        config_path = os.path.join(project_dir, 'config')
        for f in os.listdir(config_path):
            if f == 'app_cfg.py':
                return os.path.join(config_path, f)

    def _replace_css_links(self, template):
        lines = []
        with contextlib.closing(open(template)) as master:
            for line in master:
                if line.find('<link rel="stylesheet"') >= 0:
                    if line.find('/bootstrap.') >= 0:
                        lines.append(BOOTSTRAP)
                    elif line.find('/bootstrap-responsive.') >= 0:
                        lines.append(BOOTSTRAP_RESPONSIVE)
                    else:
                        lines.append(line)
                else:
                    lines.append(line)
        return ''.join(lines)

    def _append_scss_plug(self, app_config):
        with contextlib.closing(open(app_config)) as config:
            config_content = config.read()
            if 'tgext.scss' in config_content:
                return config_content

            if 'tgext.pluggable' not in config_content:
                config_content = '\n'.join([config_content, "from tgext.pluggable import plug"])

            config_content = '\n'.join([config_content, "plug(base_config, 'tgext.scss')"])
            return config_content

    def _append_scss_include_path(self, app_config):
        with contextlib.closing(open(app_config)) as config:
            config_content = config.read()
            if 'public/bootstrap/stylesheets' in config_content:
                return config_content

            append_path_content = APPEND_PATH % dict(include_path='/bootstrap/stylesheets')
            config_content = '\n'.join([config_content, append_path_content])
            return config_content

    def take_action(self, opts):
        if not os.path.exists('development.ini'):
            log.error('Must be run inside a TurboGears2 project')
            return

        project_dir, public_dir = self._find_public()
        self.run_template(public_dir, opts)

        master_templates = self._find_master_templates(project_dir)
        for master_template in master_templates:
            log.info('Patching %s template', master_template)
            master = self._replace_css_links(master_template)
            with contextlib.closing(open(master_template, 'w')) as template_file:
                template_file.write(master)

        app_cfg = self._find_app_config(project_dir)
        new_config = self._append_scss_plug(app_cfg)
        with contextlib.closing(open(app_cfg, 'w')) as config:
            log.info('Plugging tgext.scss')
            config.write(new_config)

        new_config = self._append_scss_include_path(app_cfg)
        with contextlib.closing(open(app_cfg, 'w')) as config:
            log.info('Tuning SCSS include path')
            config.write(new_config)
