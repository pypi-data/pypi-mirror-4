##############################################################################
#
# Copyright (c) 2010 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import logging
import os
from platform import uname
import setuptools
import shlex
import shutil
import subprocess
import sys
import tempfile
import zc.buildout

ARCH_MAP = {
    'i386': 'x86',
    'i586': 'x86',
    'i686': 'x86',
    'x86_64': 'x86-64'
}

OS_MAP = {
    'darwin': 'mac',
    'linux2': 'linux'
    #To be continued
}


def readElfAsDict(f):
  """Reads ELF information from file"""
  popen = subprocess.Popen(['readelf', '-d', f],
      stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  result = popen.communicate()[0]
  if popen.returncode != 0:
    raise AssertionError(result)
  library_list = []
  rpath_list = []
  runpath_list = []
  for l in result.split('\n'):
    if '(NEEDED)' in l:
      library_list.append(l.split(':')[1].strip(' []'))
    elif '(RPATH)' in l:
      rpath_list = [q.rstrip('/') for q in l.split(':', 1)[1].strip(' []'
        ).split(':')]
    elif '(RUNPATH)' in l:
      runpath_list = [q.rstrip('/') for q in l.split(':', 1)[1].strip(' []'
        ).split(':')]
  if len(runpath_list) == 0:
    runpath_list = rpath_list
  elif len(rpath_list) != 0 and runpath_list != rpath_list:
    raise ValueError('RPATH and RUNPATH are different.')
  return dict(
    library_list=sorted(library_list),
    runpath_list=sorted(runpath_list)
  )


def call(*args, **kwargs):
  """Subprocess call with closed file descriptors and stdin"""
  kwargs.update(
    stdin=subprocess.PIPE,
    close_fds=True)
  popen = subprocess.Popen(*args, **kwargs)
  popen.stdin.flush()
  popen.stdin.close()
  popen.stdin = None
  popen.communicate()
  if popen.returncode != 0:
    raise subprocess.CalledProcessError(popen.returncode, ' '.join(args[0]))


def calls(call_string, **kwargs):
  """Subprocesser caller which allows to pass arguments as string"""
  call(shlex.split(call_string), **kwargs)

def calli(*args, **kwargs):
  """Subprocesser call wich allow to pass stdin argument"""
  popen = subprocess.Popen(*args, **kwargs)
  popen.communicate()
  if popen.returncode != 0:
    raise subprocess.CalledProcessError(popen.returncode, ' '.join(args[0]))


def guessworkdir(path):
  if len(os.listdir(path)) == 1:
    return os.path.join(path, os.listdir(path)[0])
  return path

def guessPlatform():
  arch = uname()[-2]
  target = ARCH_MAP.get(arch)
  assert target, 'Unknown architecture'
  return target

def guessOperatingSystem():
  platform = sys.platform
  target = OS_MAP.get(platform)
  assert target, 'Unknown architecture'
  return target

TRUE_LIST = ('y', 'on', 'yes', 'true', '1')

class Script:
  """Free script building system"""
  def _checkPromise(self, promise_key, location):
    promise_text = self.options.get(promise_key)
    if promise_text is None:
      self.logger.warning('Warning, promise %r not defined' % promise_key)
      return True
    promise_problem_list = []
    a = promise_problem_list.append
    for promise in promise_text.split('\n'):
      promise = promise.strip()
      if not promise:
        continue
      if promise.startswith('file:') or promise.startswith('statlib'):
        s, path = promise.split(':')
        if not os.path.exists(os.path.join(location, path)):
          a('File promise not met for %r' % path)
      elif promise.startswith('directory'):
        s, path = promise.split(':')
        if not os.path.isdir(os.path.join(location, path)):
          a('Directory promise not met for %r' %
              path)
      elif promise.startswith('dynlib:'):
        if 'linked:' not in promise:
          raise zc.buildout.UserError('dynlib promise requires \'linked:\' '
            'parameter.')
        if 'rpath:' not in promise:
          rpath_list = []
        for promise_part in promise.split():
          if promise_part.startswith('dynlib:'):
            s, path = promise_part.split(':')
          elif promise_part.startswith('linked:'):
            s, link_list = promise_part.split(':')
            link_list = link_list.split(',')
          elif promise_part.startswith('rpath:'):
            s, rpath_list = promise_part.split(':')
            if rpath_list:
              r = rpath_list
              rpath_list = []
              for q in r.split(','):
                if q.startswith('!'):
                  q = q.replace('!', location)
                rpath_list.append(q)
            else:
              rpath_list = []
        if not os.path.exists(os.path.join(location, path)):
          a('Dynlib promise file not met %r' % promise)
        else:
          elf_dict = readElfAsDict(os.path.join(location, path))
          if sorted(link_list) != sorted(elf_dict['library_list']):
            a('Promise library list not met (wanted: %r, found: %r)' % (
              link_list, elf_dict['library_list']))
          if sorted(rpath_list) != sorted(elf_dict['runpath_list']):
            a('Promise rpath list not met (wanted: %r, found: %r)' % (
              rpath_list, elf_dict['runpath_list']))
      else:
        raise zc.buildout.UserError('Unknown promise %r' % promise)
    if len(promise_problem_list):
      raise zc.buildout.UserError('Promise not met, found issues:\n  %s' %
          '  '.join([q + '\n' for q in promise_problem_list]))

  def download(self, url, md5sum=None):
    download = zc.buildout.download.Download(self.buildout['buildout'],
        hash_name=True, cache=self.buildout['buildout'].get('download-cache'))
    path, is_temp = download(url, md5sum=md5sum)
    return path

  def extract(self, path):
    extract_dir = tempfile.mkdtemp(self.name)
    self.logger.debug('Created working directory %r' % extract_dir)
    setuptools.archive_util.unpack_archive(path, extract_dir)
    self.cleanup_dir_list.append(extract_dir)
    return extract_dir

  def pipeCommand(self, command_list_list, *args, **kwargs):
    """Allows to do shell like pipes (|)"""
    subprocess_list = []
    previous = None
    kwargs['stdout'] = subprocess.PIPE
    run_list = []
    for command_list in command_list_list:
      if previous is not None:
        kwargs['stdin'] = previous.stdout
      p = subprocess.Popen(command_list, *args, **kwargs)
      if previous is not None:
        previous.stdout.close()
      subprocess_list.append((p, command_list))
      run_list.append(' '.join(command_list))
      previous = p
    self.logger.info('Running: %r' % ' | '.join(run_list))
    subprocess_list.reverse()
    [q[0].wait() for q in subprocess_list]
    for q in subprocess_list:
      if q[0].returncode != 0:
        raise zc.buildout.UserError('Failed while running command %r' % q[1])

  def failIfPathExists(self, path):
    if os.path.lexists(path):
      raise zc.buildout.UserError('Path %r exists, cannot continue' % path)

  def copyTree(self, origin, destination, ignore_dir_list=None):
    """Recursively Copy directory.

    ignore_dir_list is a list of relative directories you want to exclude.
    Example :
    copytree("/from", "/to", ignore_dir_list=["a_private_dir"])
    """
    # Check existence before beginning. We don't want to cleanup something
    # that does not belong to us.
    if os.path.exists(destination):
      raise shutil.Error('Destination already exists: %s' % destination)
    self.logger.info("Copying %s to %s" % (origin, destination))
    if ignore_dir_list is None:
      ignore_dir_list = []
    try:
      shutil.copytree(origin, destination,
                      ignore=lambda src, names: ignore_dir_list)
    except (shutil.Error, OSError) as error:
      # Cleanup in case of failure
      try:
        shutil.rmtree(destination, ignore_errors=True)
      except (shutil.Error, OSError), strerror:
        self.logger.error("Error occurred when cleaning after error: %s",
          strerror)
      raise error
    return True

  script = 'raise NotImplementedError'
  update_script = None

  def __init__(self, buildout, name, options):
    self.cleanup_dir_list = []
    self.options = options
    self.buildout = buildout
    self.name = name
    self.logger = logging.getLogger('SlapOS build of %s' % self.name)

    self.options.setdefault('location',
        os.path.join(buildout['buildout']['parts-directory'], self.name))

    # cleanup some variables
    for k in ['location', 'url', 'md5sum', 'path']:
      self.options[k] = self.options.get(k, '').strip()
    if self.options.get('format', 'yes') in ['y', 'yes', '1', 'on']:
        self.options['script'] = self.options.get('script', self.script) % \
          self.options
    if self.options.get('keep-on-error', '').strip().lower() in TRUE_LIST:
      self.logger.debug('Keeping directories in case of errors')
      self.keep_on_error = True
    else:
      self.keep_on_error = False
  def getEnvironment(self):
    # prepare cool dictionary
    wanted_env = {}
    for line in self.options.get('environment', '').splitlines():
      line = line.strip()
      if not line:
        continue
      if not '=' in line:
        raise zc.buildout.UserError('Line %r in environment is incorrect' %
          line)

      key, value = line.split('=', 1)
      key = key.strip()
      value = value.strip()
      if key in wanted_env:
        raise zc.buildout.UserError('Key %r is repeated' % key)
      wanted_env[key] = value
    env = {}
    for k, v in os.environ.iteritems():
      change = wanted_env.pop(k, None)
      if change is not None:
        env[k] = change % os.environ
        self.logger.info('Environment %r setup to %r' % (k, env[k]))
      else:
        env[k] = v
    for k, v in wanted_env.iteritems():
      self.logger.info('Environment %r added with %r' % (k, v))
      env[k] = v
    return env

  def install(self):
    try:
      env = self.getEnvironment()
      if os.path.exists(self.options['location']):
        self.cleanup_dir_list.append(self.options['location'])
        raise shutil.Error('Directory %s already exists' % 
            self.options['location'])
      exec self.options['script']
      try:
        self._checkPromise('slapos_promise', self.options['location'])
      except Exception:
        if os.path.exists(self.options['location']):
          self.cleanup_dir_list.append(self.options['location'])
        raise
    finally:
      for d in self.cleanup_dir_list:
        if os.path.exists(d):
          if not self.keep_on_error:
            self.logger.debug('Cleanup directory %r' % d)
            shutil.rmtree(d)
          else:
            self.logger.info('Left directory %r as requested' % d)

    return [self.options['location']]

  def update(self):
    if self.update_script is None:
      return None
    try:
      env = self.getEnvironment()
      exec self.options['update_script']
      try:
        self._checkPromise('slapos_update_promise', self.options['location'])
      except Exception:
        self.logger.info('Keeping location %r during update' %
          self.options['location'])
        raise
    finally:
      for d in self.cleanup_dir_list:
        if os.path.exists(d):
          self.logger.debug('Cleanup directory %r' % d)
          shutil.rmtree(d)

  def applyPatchList(self, patch_string, patch_options=None, patch_binary=None, cwd=None):
    if patch_string is not None:
      if patch_options is None:
        patch_options = []
      else:
        patch_options = shlex.split(patch_options)
      if patch_binary is None:
        patch_binary = 'patch'
      else:
        patch_binary = patch_binary.strip()
      kwargs = dict()
      if cwd is not None:
        kwargs['cwd'] = cwd
      for patch in patch_string.splitlines():
        patch = patch.strip()
        if patch:
          if ' ' in patch:
            patch, md5sum = patch.split(' ', 1)
            md5sum = md5sum.strip()
            if md5sum.lower() == 'unknown':
              md5sum = None
          else:
            md5sum = None
          if md5sum is not None and ' ' in md5sum:
            md5sum, patch_options = md5sum.split(' ', 1)
            patch_options = patch_options.split(' ')
          kwargs['stdin'] = open(self.download(patch, md5sum))
          self.logger.info('Applying patch %r' % patch)
          calli([patch_binary] + patch_options, **kwargs)

class Cmmi(Script):
  """Simple configure-make-make-install compatible with hexagonit.recipe.cmmi

  Compatibility on parameter level"""

  script = """
if self.options['url']:
  url = self.download(self.options['url'], self.options.get('md5sum'))
  extract_dir = self.extract(url)
  workdir = guessworkdir(extract_dir)
else:
  workdir = self.options['path']
configure_command = self.options.get('configure-command')
if configure_command is None or configure_command.lower() == 'None':
  configure_command = ["./configure", "--prefix=%(location)s"] + %(configure-options)r.split()
else:
  configure_command = configure_command.split()
self.logger.info('Configuring with: %%r' %% ' '.join(configure_command))
self.applyPatchList(self.options.get('patches'), self.options.get('patch-options'), self.options.get('patch-binary'), workdir)
call(configure_command, cwd=workdir, env=env)
make_command = [self.options.get('make-binary', "make")]
make_options = self.options.get('make-options')
if make_options is not None:
  make_command.extend(make_options.split())
self.logger.info('Building with %%r' %% ' '.join(make_command))
call(make_command, cwd=workdir, env=env)
make_command.append('install')
self.logger.info('Installing with %%r' %% ' '.join(make_command))
call(make_command + ['install'], cwd=workdir, env=env)
"""

  def __init__(self, buildout, name, options):
    options['configure-options'] = ' '.join(options.get('configure-options',
      '').strip().splitlines())
    Script.__init__(self, buildout, name, options)
    if options['url'] and options['path']:
        raise zc.buildout.UserError('You must use either "url" or "path", not both!')
    if not (options['url'] or options['path']):
        raise zc.buildout.UserError('You must provide either "url" or "path".')