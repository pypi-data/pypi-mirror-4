# -*- coding: utf8 -*-

from puke import *
import json
import airlicenses as al

AIRSTRIP_RC_PATH = '~/.airstriprc'

API = '2'

# Template for empty RC
EMPTY_RC = json.loads("""{
  "version": "",
  "company": {
    "name": "",
    "url": "",
    "mail": ""
  },
  "git": "",
  "ln": "en-us",
  "you": {
    "name": "",
    "url": "",
    "mail": ""
  },
  "license": "MIT"
}""")

class AirRC():
  def __init__(self):
    if not FileSystem.exists(AIRSTRIP_RC_PATH):
      FileSystem.writefile(AIRSTRIP_RC_PATH, json.dumps(EMPTY_RC, indent = 4))

    try:
      self.rc = json.loads(FileSystem.readfile(AIRSTRIP_RC_PATH))
    except:
      console.fail('Your airstrip rc file (%s) is horked! Please rm or fix it' % AIRSTRIP_RC_PATH)

    if not self.rc['version'] == API:
      self.__ask__()

  def __ask__(self):
    defaults = self.rc.copy()
    for i in EMPTY_RC:
      if not i in defaults:
        defaults[i] = EMPTY_RC[i]

    console.warn("""You don't seem to have documented your default informations, 
or airstrip has an upgraded version that requires new infos.""")
    console.info("""These infos are stored only in the file %s, which you can edit manually, 
are entirely optional, and used only by the airstrip "seed" command to populate package.json 
and other projects boilerplates.""" % AIRSTRIP_RC_PATH)

    console.info('First, provide informations about your company (if any - used generally for the author fields and copyright owner informations.)')
    self.rc['company']['name'] = prompt('Your company name (currently: %s)' % defaults['company']['name'], defaults['company']['name'])
    self.rc['company']['mail'] = prompt('Your company mail (currently: %s)' % defaults['company']['mail'], defaults['company']['mail'])
    self.rc['company']['url'] = prompt('Your company website / twitter (currently: %s)' % defaults['company']['url'], defaults['company']['url'])

    console.info('Now, about you - this will be used for the contributors/maintainers fields.')
    self.rc['you']['name'] = prompt('Your name (currently: %s)' % defaults['you']['name'], defaults['you']['name'])
    self.rc['you']['mail'] = prompt('Your mail (currently: %s)' % defaults['you']['mail'], defaults['you']['mail'])
    self.rc['you']['url'] = prompt('Your website / twitter (currently: %s)' % defaults['you']['url'], defaults['you']['url'])

    keys = al.AirLicenses().list()
    self.rc['license'] = prompt('Default license for new projects (among %s)? (currently: %s)' % (keys, defaults['license']), defaults['license'])

    self.rc['git'] = prompt('Default git owner to use for new projects? (currently: %s)' % defaults['git'], defaults['git'])
    self.rc['ln'] = prompt('Default language for projects? (currently: %s)' % defaults['ln'], defaults['ln'])

    self.set('version', API)

  def get(self, key):
    if key in self.rc:
      return self.rc[key]
    return None

  def set(self, key, value):
    if key:
      self.rc[key] = value
    FileSystem.writefile(AIRSTRIP_RC_PATH, json.dumps(self.rc, indent = 4))
