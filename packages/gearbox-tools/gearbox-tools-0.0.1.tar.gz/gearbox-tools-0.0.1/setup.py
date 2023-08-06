from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

version = "0.0.1"

setup(name='gearbox-tools',
      version=version,
      description="Bunch of utility commands for gearbox toolset",
      long_description=README,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='gearbox command-line commands',
      author='Alessandro Molina',
      author_email='alessandro.molina@axant.it',
      url='https://bitbucket.org/_amol_/gearbox-tools',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points={''
        'gearbox.commands': [
            'tg-hgignore = gearboxtools.tgignore:TGIgnoreCommand',
            'tg-bootstrap = gearboxtools.tgbootstrap:TGBootstrapCommand',
            'pkgdeps = gearboxtools.pkgdeps:PackageDepsCommand',
            'deploy-circus = gearboxtools.deploy_circus:CircusDeployCommand',
        ],
      })
