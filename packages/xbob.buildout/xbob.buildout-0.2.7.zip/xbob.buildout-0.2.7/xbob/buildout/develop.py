#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon  4 Feb 09:24:35 2013 CET

"""Compiles a Python/C++ egg extension for Bob
"""

import os
import logging
from . import tools
from zc.recipe.egg.custom import Develop

class Recipe(Develop):
  """Compiles a Python/C++ egg extension for Bob
  """

  def __init__(self, buildout, name, options):

    self.name, self.options = name, options
    self.logger = logging.getLogger(self.name)
    self.buildout = buildout

    # finds the setup script or use the default
    options['setup'] = os.path.join(buildout['buildout']['directory'],
        options.get('setup', '.'))

    # gets a personalized prefixes list or the one from buildout
    prefixes = tools.parse_list(options.get('prefixes', ''))
    if not prefixes:
      prefixes = tools.parse_list(buildout['buildout'].get('prefixes', ''))

    # set the pkg-config paths to look at
    pkgcfg = [os.path.join(k, 'lib', 'pkgconfig') for k in prefixes]
    self.pkgcfg = [os.path.abspath(k) for k in pkgcfg if os.path.exists(k)]

    Develop.__init__(self, buildout, name, options)

  def _set_environment(self):
    """Sets the current environment for variables needed for the setup of the
    package to be compiled"""

    self._saved_environment = {}

    if self.pkgcfg:

      self._saved_environment['PKG_CONFIG_PATH'] = os.environ.get('PKG_CONFIG_PATH', None)

      tools.prepend_env_paths('PKG_CONFIG_PATH', self.pkgcfg)
      self.logger.debug('PKG_CONFIG_PATH=%s' % os.environ['PKG_CONFIG_PATH'])
      for k in reversed(self.pkgcfg):
        self.logger.info("Adding pkg-config path '%s'" % k)

  def _restore_environment(self):
    """Resets the environment back to its previous state"""

    for key in self._saved_environment:
      if self._saved_environment[key] is None:
        try:
          del os.environ[key]
        except KeyError:
          pass
      else:
        os.environ[key] = self._saved_environment[key]
        del self._saved_environment[key]

  # a modified copy of zc.buildout.easy_install.develop
  def install(self):

    return Develop.install(self)

  update = install
