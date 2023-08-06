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
import os
import shutil
import zc.buildout

class Recipe(object):
  _parts = None

  def __init__(self, buildout, name, options):
    buildout_section = buildout['buildout']
    self._downloader = zc.buildout.download.Download(buildout_section,
      hash_name=True)
    self._url = options['url']
    self._md5sum = options.get('md5sum')
    mode = options.get('mode')
    if mode is not None:
      mode = int(mode, 8)
    self._mode = mode
    if 'filename' in options and 'destination' in options:
      raise zc.buildout.UserError('Parameters filename and destination are '
        'exclusive.')
    destination = options.get('destination', None)
    if destination is None:
      self._parts = parts = os.path.join(buildout_section['parts-directory'],
        name)
      destination = os.path.join(parts, options.get('filename', name))
      # Compatibility with other recipes: expose location
      options['location'] = parts
    options['target'] = self._destination = destination

  def install(self):
    destination = self._destination
    result = [destination]
    parts = self._parts
    if parts is not None and not os.path.isdir(parts):
      os.mkdir(parts)
      result.append(parts)
    path, _ = self._downloader(self._url, md5sum=self._md5sum)
    if os.path.exists(destination):
      os.unlink(destination)
    shutil.copy(path, destination)
    mode = self._mode
    if mode is not None:
      os.chmod(destination, mode)
    return result

  update = install
