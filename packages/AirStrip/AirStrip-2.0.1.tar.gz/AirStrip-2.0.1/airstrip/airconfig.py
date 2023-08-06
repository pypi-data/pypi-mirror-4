# -*- coding: utf8 -*-

from puke import *
import json
import os

# That file is meant to manipulate the airstrip configuration in the scope of the current project
# That project configuration by-default use the airstrip global configuration
# Possibly overriden by specific elements in the airconfig file in cwd.
AIRSTRIP_ROOT = os.path.dirname(os.path.realpath(__file__))
# Should point to the globally installed airstrip configuration file
AIRSTRIP_CONFIG_PATH = os.path.join(AIRSTRIP_ROOT, 'global.json')
# The project in the current directory airconfig file, if any
PROJECT_CONFIG_PATH = './airfile.json'


class AirConfig():
  def __init__(self):
    self.general = json.loads(FileSystem.readfile(AIRSTRIP_CONFIG_PATH))
    self.project = self._load_()

  def _load_(self):
    ret = json.loads('{}')
    if FileSystem.exists(PROJECT_CONFIG_PATH):
      try:
        d = json.loads(FileSystem.readfile(PROJECT_CONFIG_PATH))
        if 'config' in d:
          ret = d['config']
      except:
        console.error('Your project file configuration is horked and has been ignored!')
    return ret

  def _save_(self, data):
    original = json.loads('{}')
    if FileSystem.exists(PROJECT_CONFIG_PATH):
      try:
        original = json.loads(FileSystem.readfile(PROJECT_CONFIG_PATH))
      except:
        pass
    original['config'] = data

    FileSystem.writefile(PROJECT_CONFIG_PATH, json.dumps(original, indent=4))


  def list(self):
    for i in self.general:
      value = self.general[i]['default']
      if i in self.project:
        value = '%s (default: %s)' % (self.project[i], self.general[i]['default'])
      print '%s: %s [%s]' % (i, value, self.general[i]['info'])


  def get(self, key):
    if not key in self.general:
      console.error('No such configuration flag (%s)' % key);
      return
    if key in self.project:
      return self.project[key]
    return self.general[key]['default']

  def override(self, key, value):
    if not key in self.general:
      console.error('You are tryin to set a configuration switch that does not exist (%s)' % key);
      return
    if key in self.project:
      # Same value, ignore
      if value == self.project[key]:
        console.error('Ignoring unchanged property %s (value is already %s)' % (key, value))
        return
      # Default value, remove from self.project settings
      if self.general[key]['default'] == value:
        self.project.pop(key, None)
      # Otherwise change self.project key override
      else:
        self.project[key] = value
    elif self.general[key]['default'] == value:
      console.error('Ignoring unchanged property %s (default is already %s)' % (key, value))
      return
    else:
      self.project[key] = value

    self._save_(self.project)

    console.info('Configuration switch "%s" has been set to "%s"' % (key, value))
