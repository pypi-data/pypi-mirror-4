# -*- coding: utf-8 -*-
from ConfigParser import ConfigParser
import logging as log
import subprocess
import urllib
import sys
import os
import re

__doc__ = """Contains console scripts entry points for gp.bootstrap
"""

BUILDOUT_CFG = '''[buildout]
newest = false
prefer-final = true
parts = eggs
develop = .

[eggs]
recipe = zc.recipe.egg
initialization =
entry-points =
eggs =


'''

DEFAULT_CFG = '''[buildout]
eggs-directory = %s

''' % os.path.expanduser('~/eggs')

_re_interpreter = re.compile(r'[23]{1}\.[0-9]{1}')


def main():
    """main script
    """

    verbose = '-v' in sys.argv
    log.basicConfig(stream=sys.stderr,
                    format=verbose and '%(message)s' or '%(message)s',
                    level=verbose and log.DEBUG or log.INFO)

    buildout_dir = os.path.expanduser('~/.buildout')
    if not os.path.isdir(buildout_dir):
        os.makedirs(buildout_dir)

    default_cfg = os.path.join(buildout_dir, 'default.cfg')
    if not os.path.isfile(default_cfg):
        log.info('Creating %s', default_cfg)
        open(default_cfg, 'w').write(DEFAULT_CFG)
    defaults = ConfigParser()
    defaults.read(default_cfg)
    eggs_directory = defaults.get('buildout', 'eggs-directory')
    log.debug('Eggs found at %s', eggs_directory)

    template_cfg = os.path.join(buildout_dir, 'template.cfg')
    if not os.path.isfile(template_cfg):
        log.info('Creating %s', template_cfg)
        open(template_cfg, 'w').write(BUILDOUT_CFG)

    digits = [d for d in sys.argv[1:] if _re_interpreter.match(d)]

    if digits:
        sys.argv.remove(digits[0])
        interpreter = 'python'+digits[0]
    else:
        interpreter = sys.executable
    log.info('Using %s', interpreter)

    bootstrap_url = ('https://github.com/buildout/buildout/'
                     'raw/2/bootstrap/bootstrap.py')
    bootstrap_script = 'bootstrap.py'
    buildout_cfg = 'buildout.cfg'

    if not os.path.isfile(bootstrap_script):
        log.debug('Fetching %s', bootstrap_url)
        page = urllib.urlopen(bootstrap_url)
        open(bootstrap_script, 'w').write(page.read())

    if not os.path.isfile(buildout_cfg):
        open(buildout_cfg, 'w').write(open(template_cfg).read())

    log.debug('Running %s', bootstrap_script)
    subprocess.call([interpreter, bootstrap_script,
                    '--eggs=%s' % eggs_directory,
                    '-c', buildout_cfg, '-d'])
    log.debug('Running bin/buildout with %s', buildout_cfg)
    subprocess.call(['bin/buildout', '-c', buildout_cfg] + sys.argv[1:])
