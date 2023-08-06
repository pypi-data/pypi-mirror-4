import shutil
from gearbox.command import TemplateCommand

class TGIgnoreCommand(TemplateCommand):
    def get_description(self):
        return 'Adds hgignore for TurboGears projects'

    def get_parser(self, prog_name):
        parser = super(TGIgnoreCommand, self).get_parser(prog_name)
        return parser

    def take_action(self, opts):
        self.run_template('.', opts)
        shutil.move('hgignore', '.hgignore')