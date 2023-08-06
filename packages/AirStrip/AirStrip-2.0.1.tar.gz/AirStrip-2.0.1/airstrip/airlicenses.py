# -*- coding: utf8 -*-

from puke import *
import os

AIRSTRIP_ROOT = os.path.dirname(os.path.realpath(__file__))

# System-wide yawns path
AIRSTRIP_LICENSES = FileSystem.join(AIRSTRIP_ROOT, 'licenses')

# Template for empty RC
EMPTY_LICENSE = """http://licenseurl

Licensed under the {key} license.

License text, bla."""

class AirLicenses():
  def __init__(self):
    self.licences = {}
    for i in FileList(AIRSTRIP_LICENSES).get():
      d = FileSystem.readfile(i).split('\n\n')
      licenseurl = d.pop(0)
      licensecontent = ('\n\n').join(d)
      self.licences[FileSystem.basename(i).split('.').pop(0).upper()] = {"url": licenseurl, "content": licensecontent}

  def get(self, key):
    key = key.upper()
    if key in self.licences:
      return self.licences[key]
    return False

  def edit(self, key):
    key = key.upper()
    p = FileSystem.join(AIRSTRIP_LICENSES, key)
    # Kind of dirty hack to have it in the git local repo instead of system-wide
    if FileSystem.exists('airstrip/licenses'):
      p = FileSystem.join('airstrip/licenses', key)

    if not key in self.licences:
      FileSystem.writefile(p, EMPTY_LICENSE.replace('{key}', key))
    sh('open "%s"' % p, output = False)

  def list(self):
    return self.licences.keys()
