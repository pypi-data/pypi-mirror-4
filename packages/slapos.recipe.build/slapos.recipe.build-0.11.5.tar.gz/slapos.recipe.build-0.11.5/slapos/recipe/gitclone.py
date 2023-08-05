##############################################################################
#
# Copyright (c) 2012 Vifib SARL and Contributors. All Rights Reserved.
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

import hashlib
import os
import shutil
import time
import traceback

from zc.buildout import UserError
from subprocess import check_call, CalledProcessError

try:
  try:
    from slapos.networkcachehelper import \
       helper_upload_network_cached_from_directory, \
       helper_download_network_cached_to_directory
  except ImportError:
    LIBNETWORKCACHE_ENABLED = False
  else:
    LIBNETWORKCACHE_ENABLED = True
except:
  print 'There was problem while trying to import slapos.libnetworkcache:'\
      '\n%s' % traceback.format_exc()
  LIBNETWORKCACHE_ENABLED = False
  print 'Networkcache forced to be disabled.'

GIT_DEFAULT_REMOTE_NAME = 'origin'
GIT_DEFAULT_BRANCH_NAME = 'master'
TRUE_VALUES = ['y', 'yes', '1', 'true']

GIT_CLONE_ERROR_MESSAGE = 'Impossible to clone repository.'
GIT_CLONE_CACHE_ERROR_MESSAGE = 'Impossible to clone repository and ' \
    'impossible to download from cache.'

def upload_network_cached(path, name, revision, networkcache_options):
  """
  Creates uploads repository to cache.
  """
  if not (LIBNETWORKCACHE_ENABLED and networkcache_options.get(
      'shacache-cert-file')):
    return False
  try:
    print 'Uploading git repository to cache...'
    metadata_dict = {
        'revision':revision,
        # XXX: we set date from client side. It can be potentially dangerous
        # as it can be badly configured.
        'timestamp':time.time(),
    }
    helper_upload_network_cached_from_directory(
        path=path,
        directory_key='git-buildout-%s' % hashlib.md5(name).hexdigest(),
        metadata_dict=metadata_dict,
        # Then we give a lot of not interesting things
        dir_url=networkcache_options.get('upload-dir-url'),
        cache_url=networkcache_options.get('upload-cache-url'),
        signature_private_key_file=networkcache_options.get(
            'signature-private-key-file'),
        shacache_cert_file=networkcache_options.get('shacache-cert-file'),
        shacache_key_file=networkcache_options.get('shacache-key-file'),
        shadir_cert_file=networkcache_options.get('shadir-cert-file'),
        shadir_key_file=networkcache_options.get('shadir-key-file'),
    )
    print 'Uploaded git repository to cache.'
  except Exception:
    print 'Unable to upload to cache:\n%s.' % traceback.format_exc()


def download_network_cached(path, name, revision, networkcache_options):
  """
  Download a tar of the repository from cache, and untar it.
  """
  def strategy(entry_list):
    """
    Get the latest entry.
    """
    timestamp = 0
    best_entry = None
    for entry in entry_list:
      if entry['timestamp'] > timestamp:
        best_entry = entry
    return best_entry

  return helper_download_network_cached_to_directory(
      path=path,
      directory_key='git-buildout-%s' % hashlib.md5(name).hexdigest(),
      wanted_metadata_dict={'revision':revision},
      required_key_list=['timestamp'],
      strategy=strategy,
      # Then we give a lot of not interesting things
      dir_url=networkcache_options.get('download-dir-url'),
      cache_url=networkcache_options.get('download-cache-url'),
      signature_certificate_list=\
          networkcache_options.get('signature-certificate-list'),
  )

class Recipe(object):
  """Clone a git repository."""

  def __init__(self, buildout, name, options):
    options.setdefault('location',
        os.path.join(buildout['buildout']['parts-directory'], name))
    self.repository = options.get('repository')
    self.branch = options.get('branch', GIT_DEFAULT_BRANCH_NAME)
    self.revision = options.get('revision')
    self.git_command = options.get('git-executable', 'git')
    self.name = name
    self.location = options.get('location')
    # Set boolean values
    for key in ['develop', 'forbid-download-cache']:
      attribute = key.replace('-', '_')
      if options.get(key) in TRUE_VALUES:
        setattr(self, attribute, True)
      else:
        setattr(self, attribute, False)

    self.networkcache = buildout.get('networkcache', {})

    # Check if input is correct
    if not self.repository:
      raise UserError('repository parameter is mandatory.')
    if self.revision and self.branch != GIT_DEFAULT_BRANCH_NAME:
      # revision and branch options are incompatible
      raise UserError('revision and branch (other than master) parameters '
          'are set but are incompatible. Please specify only one of them.')

  def gitReset(self, revision=None):
    """Operates git reset on the repository."""
    command = [self.git_command, 'reset', '--hard']
    if revision:
      command.append(revision)
    check_call(command, cwd=self.location)


  def install(self):
    """
    Do a git clone.
    If branch is specified, checkout to it.
    If revision is specified, reset to it.
    If something fails, try to download from cache.
    Else, if possible, try to upload to cache.
    """
    # If directory already exist: delete it.
    if os.path.exists(self.location):
      print 'destination directory already exists. Deleting it.'
      shutil.rmtree(self.location)

    git_clone_command = [self.git_command, 'clone',
                self.repository,
                self.location]
    if self.branch:
      git_clone_command.extend(['--branch', self.branch])

    try:
      check_call(git_clone_command)
      if not os.path.exists(self.location):
        raise UserError("Unknown error while cloning repository.")
      if self.revision:
        self.gitReset(self.revision)
      upload_network_cached(self.location, self.name, self.revision,
          self.networkcache)
    except CalledProcessError:
      print ("Unable to download from git repository. Trying from network "
          "cache...")
      if os.path.exists(self.location):
        shutil.rmtree(self.location)
      if self.forbid_download_cache:
        raise UserError(GIT_CLONE_ERROR_MESSAGE)
      if not download_network_cached(self.location, self.name, self.revision,
          self.networkcache):
        raise UserError(GIT_CLONE_CACHE_ERROR_MESSAGE)

    return [self.location]


  def update(self):
    """
    Do a git fetch.
    If user doesn't develop, reset to remote revision (or branch if revision is
    not specified).
    """
    check_call([self.git_command, 'fetch', '--all'], cwd=self.location)

    # If develop parameter is set, don't reset/update.
    # Otherwise, reset --hard
    if not self.develop:
      if self.revision:
        self.gitReset(self.revision)
      else:
        self.gitReset('@{upstream}')
