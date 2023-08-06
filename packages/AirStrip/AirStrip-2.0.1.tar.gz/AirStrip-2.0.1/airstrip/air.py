from puke import *
import json
import os
import re
from distutils import version
from verlib import NormalizedVersion
from distutils.version import StrictVersion, LooseVersion

AIRSTRIP_ROOT = os.path.dirname(os.path.realpath(__file__))
NORMALIZE_VERSION = re.compile(r'([^\d]*)')

# System-wide yawns path
AIRSTRIP_YAWN_PATH = os.path.join(AIRSTRIP_ROOT, 'airs')

# Project user-defined yawns path
PROJECT_YAWN_PATH = './airs'

EMPTY_GLOBAL = """
      "description": "",
      "keywords": [],
      "author": [],
      "licenses": [],
      "category": "library",
      "homepage": "http://",
      "tools": [],
      "depends": {},
      "strict": true,
      "git": "",
      "versions": {
        "master": {
          "package": "", 
          "resources": {
          },
          "build": [],
          "productions": {
          }
        }
      }
}"""


EMPTY_LOCAL_VERSION = """{
  "versions": {
    "version.name": {
      "package": "", 
      "resources": {
      },
      "build": [],
      "productions": {
      }
    }
  }
}"""

class Air():
  def __init__(self, name):
    self.name = name
    self.hasGlobal = False
    self.yawn = json.loads("""{
      "name": "%s",
      %s""" % (name, EMPTY_GLOBAL))

    systemPath = FileSystem.join(AIRSTRIP_YAWN_PATH, '%s.json' % name)
    if FileSystem.exists(systemPath):
      try:
        self.yawn = json.loads(FileSystem.readfile(systemPath))
        self.hasGlobal = True
      except:
        console.error('The system yawn descriptor for %s is borked!' % name)

    self.hasLocal = False
    self.local = json.loads('{}')
    localPath = FileSystem.join(PROJECT_YAWN_PATH, '%s.json' % name)
    if FileSystem.exists(localPath):
      try:
        self.local = json.loads(FileSystem.readfile(localPath))
        self.hasLocal = True
      except:
        console.error('The yawn descriptor for %s in your project is borked!' % name)


  @staticmethod
  def exists(name):
    systemPath = FileSystem.join(AIRSTRIP_YAWN_PATH, '%s.json' % name)
    localPath = FileSystem.join(PROJECT_YAWN_PATH, '%s.json' % name)
    if not FileSystem.exists(localPath) and not FileSystem.exists(systemPath):
      return False
    return True



  def edit(self, globally = False):
    # Global edition, just go
    if globally:
      p = FileSystem.join(AIRSTRIP_YAWN_PATH, '%s.json' % self.name)
      c = self.yawn
    else:
      p = FileSystem.join(PROJECT_YAWN_PATH, '%s.json' % self.name)
      # No local data yet
      if not self.hasLocal:
        # if no global data either, populate with yawn
        if not self.hasGlobal:
          self.local = json.loads("""{
            "name": "%s",
            %s""" % (self.name, EMPTY_GLOBAL))
        # if has global data, should start empty instead, as a version specialization
        else:
          self.local = json.loads(EMPTY_LOCAL_VERSION)
      c = self.local

    if not FileSystem.exists(p):
      FileSystem.writefile(p, json.dumps(c, indent=4))
    sh('open "%s"' % p)
    self.__init__(self.name)

  def get(self, version, key = False):
    if key == "safename":
      return self.name
    keys = ['name', 'homepage', 'git', 'description', 'author', 'keywords', 'strict', 'licenses', 'category', 'tools', 'depends', 'package', 'resources', 'build', 'productions']

    #, 'versions']
    # if key and not key in keys:
    #   console.error('There is no such thing as %s' % key)

    if self.hasGlobal and (version in self.yawn["versions"]):
      ref = self.yawn['versions'][version]
      if "package.json" in ref and "component.json" in ref:
        for i in ref["component.json"]:
          ref["package.json"][i] = ref["component.json"][i]
      parent = self.yawn
    elif self.hasLocal and (version in self.local["versions"]):
      ref = self.local['versions'][version]
      if "package.json" in ref and "component.json" in ref:
        for i in ref["component.json"]:
          ref["package.json"][i] = ref["component.json"][i]
      parent = self.local
    else:
      console.error('The requested version (%s) does not exist' % version)
      raise Exception("FAIL")

    if not key:
      return ref
    if key in ref:
      return ref[key]
    if "package.json" in ref and key in ref["package.json"]:
      return ref["package.json"][key]

    if not key in parent:
      if "branch" in ref:
        return self.get(ref["branch"], key)
      else:
        console.warn('No such key (%s)' % key)
        return False
    return parent[key]

  def versions(self):
    r = re.compile(r'([^\d]*)')
    versions = {}
    result = []
    dates = {}

    if self.hasGlobal:
      self._parseVersions(self.yawn["versions"], versions)
      # print(self.yawn["versions"])
    if self.hasLocal:
      self._parseVersions(self.local["versions"], versions)
      
    hasMaster = versions.pop('master', False)
    
    sortedVersions = versions.keys()
    sortedVersions.sort(key=LooseVersion)

    for key in sortedVersions:
      result.append(versions[key])

    if hasMaster:
      result.append(hasMaster)

    return result

  def _parseVersions(self, entries, result):
    for version in entries:
      date = False
      content = entries[version]

      if 'date' in content and 'commited' in content['date']:
        date = content['date']['commited']
      
      if not date:
        date = None

      if version == 'master':
        normalized = 'master'
      else:
        normalized = NORMALIZE_VERSION.sub('', version, 1)
        
      result[normalized] = (version, date)

  # def latest(self):
  #   v = self.versions()
  #   for i in v:
  #     v = i.lstrip("v")
  #     better = re.sub(r"([0-9]+)[.]([0-9]+)[.]([0-9]+)(.*)$", r"\1 \2 \3 \4", v).split(" ")
  #     print better
      # try:
      #   print NormalizedVersion(v)
      # except:
      #   print v.split('.')
      #   print "WRONG version"
# http://www.python.org/dev/peps/pep-0386/#normalizedversion
      # version.StrictVersion('1.0.5') < version.StrictVersion('1.0.8')
      # print version.StrictVersion(i)

      # print better
    # if self.hasGlobal:
    #   if key in self.yawn:
    #     ref = self.yawn[key]

    # if self.hasGlobal:
    #   ref = 
    #   return self.yawn[key]
    # if self.hasLocal:
    #   return self.local[key]
    # idx = keys.index(key)
    # types = ['', '', [], [], '', [], {}, '', {}, [], {}]
    # return types[idx]



