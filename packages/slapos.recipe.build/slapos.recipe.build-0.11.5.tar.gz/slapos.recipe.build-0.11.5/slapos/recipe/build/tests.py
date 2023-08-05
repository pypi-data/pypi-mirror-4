from zope.testing import doctest
from zope.testing import renormalizing

import os
import re
import shutil
import stat
import tempfile
import unittest
import zc.buildout.testing
import zc.buildout.tests

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

GIT_REPOSITORY = 'http://git.erp5.org/repos/slapos.recipe.build.git'
BAD_GIT_REPOSITORY = 'http://git.erp5.org/repos/nowhere'
REVISION = '2566127'

def setUp(test):
  zc.buildout.testing.buildoutSetUp(test)
  zc.buildout.testing.install_develop('slapos.recipe.build', test)

class GitCloneNonInformativeTests(unittest.TestCase):

  def setUp(self):
    self.dir = os.path.realpath(tempfile.mkdtemp())

  def tearDown(self):
    shutil.rmtree(self.dir)
    for var in os.environ.keys():
      if var.startswith('SRB_'):
        del os.environ[var]

  def write_file(self, filename, contents, mode=stat.S_IREAD | stat.S_IWUSR):
    path = os.path.join(self.dir, filename)
    fh = open(path, 'w')
    fh.write(contents)
    fh.close()
    os.chmod(path, mode)
    return path

  def make_recipe(self, buildout, name, options):
    from slapos.recipe.gitclone import Recipe
    parts_directory_path = os.path.join(self.dir, 'test_parts')

    bo = {
        'buildout': {
            'parts-directory': parts_directory_path,
            'directory': self.dir,
         }
    }
    bo.update(buildout)
    return Recipe(bo, name, options)

  def test_using_download_cache_if_git_fails(self):
    from slapos.recipe.gitclone import GIT_CLONE_ERROR_MESSAGE, \
        GIT_CLONE_CACHE_ERROR_MESSAGE
    recipe = self.make_recipe({}, 'test', {
        'repository': BAD_GIT_REPOSITORY,
        'forbid-download-cache': 'false',
    })
    os.chdir(self.dir)
    try:
      recipe.install()
      # Should have raised before.
      self.assertTrue(False)
    except zc.buildout.UserError, e:
      self.assertEquals(e.message, GIT_CLONE_CACHE_ERROR_MESSAGE)

  def test_not_using_download_cache_if_forbidden(self):
    from slapos.recipe.gitclone import GIT_CLONE_ERROR_MESSAGE, \
        GIT_CLONE_ERROR_MESSAGE
    recipe = self.make_recipe({}, 'test', {
        'repository': BAD_GIT_REPOSITORY,
        'forbid-download-cache': 'true',
    })
    os.chdir(self.dir)
    try:
      recipe.install()
      # Should have raised before.
      self.assertTrue(False)
    except zc.buildout.UserError, e:
      self.assertEquals(e.message, GIT_CLONE_ERROR_MESSAGE)

def test_suite():
  suite = unittest.TestSuite((
      doctest.DocFileSuite(
          'README.rst',
          module_relative=False,
          setUp=setUp,
          tearDown=zc.buildout.testing.buildoutTearDown,
          optionflags=optionflags,
          checker=renormalizing.RENormalizing([
              zc.buildout.testing.normalize_path,
              (re.compile(r'http://localhost:\d+'), 'http://test.server'),
              # Clean up the variable hashed filenames to avoid spurious
              # test failures
              (re.compile(r'[a-f0-9]{32}'), ''),
              ]),
          ),
      unittest.makeSuite(GitCloneNonInformativeTests),
      ))
  return suite

if __name__ == '__main__':
  unittest.main(defaultTest='test_suite')
