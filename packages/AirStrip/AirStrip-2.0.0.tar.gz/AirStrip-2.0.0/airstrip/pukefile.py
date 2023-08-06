#!/usr/bin/env puke
# -*- coding: utf8 -*-
from puke.Task import task
global console, FileSystem
from puke import console, FileSystem, sh, deepcopy
global dateutil, datetime
import dateutil.parser
import datetime

global json
import json

# import airfile
global re
import re

global yawn
import air as yawn

global airc
import airconfig as airc

global airf
import airfile as airf

global airb
import airbuild as airb

global gh
import githelper as gh

global ge
import github as ge

global se
import seeder as se

global lic
import airlicenses as lic


@task("Manage available airstrip licenses for projects")
def license(command = False, key = False):
  airlic = lic.AirLicenses()
  if not command or command == 'list':
    print airlic.list()
  elif command == 'edit':
    airlic.edit(key)
  else:
    d = airlic.get(command)
    print "License name: %s" % command.upper()
    print "License url: %s" % d["url"]
    print "License text: %s" % d["content"]



@task("Show current configuration details (airstrip use), or set a configuration flag (airstrip use key value)")
def use(key = False, value = False):
  a = airc.AirConfig()
  if key == False:
    a.list()
  else:
    if not value == False:
      if value.lower() == "true":
        value = True
      # Doesn't f**** work like it should
      elif value.lower() == "false":
        value = False
    a.override(key, value)


@task("Show project required libraries (airstrip require), or add a new library to the list of project dependencies (airstrip require somelibrary), possibly in a specific version (airstrip require somelibrary somversion)")
def require(key = False, version = False):
  a = airf.AirFile()
  if key == False:
    a.list()
  else:
    if not version:
      version = "master"
    # Get a yawn
    if not yawn.Air.exists(key):
      console.fail('No library by that name (%s)!' % key) 
    aero = yawn.Air(key)

    if not version == 'all':
      # Will fail if there is no such version
      aero.get(version, 'name')
      # Otherwise ok!
      a.require(key, version)
    else:
      for i in aero.versions():
        a.require(key, i)


@task("Remove a previously required library from the list of project dependencies (airstrip remove somelibrary), possibly a specific version of it (airstrip remove somelibrary someversion)")
def remove(key, version = False):
  a = airf.AirFile()
  a.remove(key, version)

@task("Edit a library description file (airstrip edit somelibrary). Passing true as second argument edits the descriptor globally.")
def edit(name, globally = False):
  if not globally == False:
    globally = True

  a = yawn.Air(name)
  # Doesn't f**** work like it should
  a.edit(globally)

@task("Show all available libraries (airstrip show), or detailed informations about a specific library (airstrip show somelibrary)")
def show(name = False):
  if not name:
    p = os.path.dirname(os.path.realpath(__file__))
    l = puke.FileList(puke.FileSystem.join(p, 'airs'), filter = "*.json")
    for i in l.get():
      print i.split('/').pop().split('.').pop(0)

    l = puke.FileList('airs', filter = "*.json")
    for i in l.get():
      print i.split('/').pop().split('.').pop(0)

    return
  # XXXX dirty hack
  # name = name.split('/').pop().replace('.json', '')
  if not yawn.Air.exists(name):
    console.fail('No library by that name (%s)!' % name) 
  a = yawn.Air(name)

  nomasterhack = "master"
  try:
    a.get('master', 'name')
  except:
    nomasterhack = a.versions().pop()


  console.info('*********************')
  console.info(a.get(nomasterhack, 'name'))
  console.info('*********************')
  console.info(a.get(nomasterhack, 'description'))
  console.info('*********************')
  # console.info(' - Category: %s' % a.get('master', 'category'))
  console.info(' - Keywords: %s' % a.get(nomasterhack, 'keywords'))
  console.info(' - Homepage: %s' % a.get(nomasterhack, 'homepage'))
  console.info(' - Author: %s' % a.get(nomasterhack, 'author'))
  console.info(' - Licenses: %s' % a.get(nomasterhack, 'licenses'))
  # console.info(' - Required tools to build: %s' % a.get('master', 'tools'))
  console.info('*********************')
  console.info('Available versions:')
  
  versions = a.versions()
  listOfVersions = tuple(x[0] for x in versions)
  maxLength = len(max(listOfVersions, key=len))

  for (i, date) in versions:
    try:
      date = dateutil.parser.parse(date)
      date = datetime.datetime.strftime(date, '%d. %B %Y')
    except:
      date = 'Unkown date'
    console.info(' * %s %s | %s' % ( str(i), " " * (maxLength - len(i)), date))

@task("Search packages for a given search string")
def search():
  pass

@task("Initialize new project")
def seed(app = False, mobile = False):
  s = se.Seeder()
  s.project()
  # XXX to be completed
  # executeTask('require', 'jasmine', 'master')
  # executeTask('build')


# @task("List all avalaible libraries")
# def list():
#   p = os.path.dirname(os.path.realpath(__file__))
#   l = puke.FileList(puke.FileSystem.join(p, 'airs'), filter = "*.json")
#   for i in l.get():
#     print i.split('/').pop().split('.').pop(0)

#   l = puke.FileList('airs', filter = "*.json")
#   for i in l.get():
#     print i.split('/').pop().split('.').pop(0)


@task("Search for a given library")
# XXX this is dumb for now
def search(key):
  cachesearch = {}
  result = []
  p = os.path.dirname(os.path.realpath(__file__))
  l = puke.FileList(puke.FileSystem.join(p, 'airs'), filter = "*.json")
  for i in l.get():
    d = puke.FileSystem.readfile(i)
    if key in d:
      result.append(i.split('/').pop().split('.').pop(0))

  for i in result:
    print i



@task("Init an air from github")
def init(owner, repo, name = False):
  g = ge.GitHubInit()
  if not name:
    name = repo
  g.retrieve(owner, repo, "airs", name)
  # # g.retrieve("documentcloud", "backbone", "airstrip/airs", "backbone")
  # # g.retrieve("twitter", "bootstrap", "airstrip/airs", "bootstrap")
  # g.retrieve("emberjs", "ember.js", "airstrip/airs", "ember")
  # g.retrieve("h5bp", "html5-boilerplate", "airstrip/airs", "h5bp")
  # g.retrieve("wycats", "handlebars.js", "airstrip/airs", "handlebars")
  # # g.retrieve("jquery", "jquery", "airstrip/airs", "jquery")
  # g.retrieve("necolas", "normalize.css", "airstrip/airs", "normalize")
  # # g.retrieve("madrobby", "zepto", "airstrip/airs", "zepto")

@task("Refresh all airs")
def reinit():
  g = ge.GitHubInit()

  p = os.path.dirname(os.path.realpath(__file__))
  l = puke.FileList(puke.FileSystem.join(p, 'airs'), filter = "*.json")
  for i in l.get():
    name = i.split('/').pop().split('.').pop(0)
    v = json.loads(puke.FileSystem.readfile(i))['git'].split('/')
    repo = v.pop()
    owner = v.pop()
    # print owner, repo, name
    g.retrieve(owner, repo, "airs", name)

  l = puke.FileList('airs', filter = "*.json")
  for i in l.get():
    name = i.split('/').pop().split('.').pop(0)
    v = json.loads(puke.FileSystem.readfile(i))['git'].split('/')
    repo = v.pop()
    owner = v.pop()
    g.retrieve(owner, repo, "airs", name)


@task("Build the list of required libraries, or a specifically required library")
def build(name = False):
  a = airf.AirFile()

  requested = a.requiredLibraries()

  config = airc.AirConfig()
  conftmp = config.get('temporary')
  confdestination = config.get('output')


  if name:
    # Check the library exists and is required
    if not yawn.Air.exists(name):
      console.fail('No library by that name (%s)!' % name) 
    if not a.isRequired(name):
      console.fail('You have not required that library (%s)!' % name) 

    # Build temporary and destination paths for the library

    yawnie = yawn.Air(name)

    nomasterhack = "master"
    try:
      yawnie.get('master', 'name')
    except:
      nomasterhack = yawnie.versions().pop()


    tmp = FileSystem.join(conftmp, yawnie.get(nomasterhack, "safename"))
    destination = FileSystem.join(confdestination, yawnie.get(nomasterhack, "safename"))
    # giti = yawnie.get('master', 'git')
    # Get each version informations json
    # vinfos = {}
    # for version in requested[name]:
    #   vinfos[version] = yawnie.get(version)

    buildit(yawnie, requested[name], tmp, destination)



    return
    # airb.build(owner, name, libs[name], tmp, destination)
    # return

    # for version in requested[name]:
    #   # category = y.get(version, 'category')
    #   destination = FileSystem.join(config.get('output'), name, version)#category, 

    #   data = y.get(version)
    #   if ".travis.yml" in data:
    #     airb.buildtravis(name, version, data[".travis.yml"], tmp, destination)
    #     print data
    #     return
        # print "version %s is OK travis: %s" % (version, data[".travis.yml"])
      # else:
      #   # Try as smart as possible?
      #   if data["tree"]
      #   print "version %s is KO travis" % (version)
                # "node_js": [
                #     0.6
                # ], 
                # "language": "node_js", 
                # "script": "script/test"


      # airb.buildone(tmp, name, version, y.get(version, 'resources'), y.get(version, 'build'), #category, 
      #     y.get(version, 'productions'), destination, y.get(version, 'strict'))
  else:
    for name in requested:

      yawnie = yawn.Air(name)

      nomasterhack = "master"
      try:
        yawnie.get('master', 'name')
      except:
        nomasterhack = yawnie.versions().pop()

      tmp = FileSystem.join(conftmp, yawnie.get(nomasterhack, "safename"))
      destination = FileSystem.join(confdestination, yawnie.get(nomasterhack, "safename"))
      # giti = yawnie.get('master', 'git')
      # Get each version informations json
      # vinfos = {}
      # for version in requested[name]:
      #   vinfos[version] = yawnie.get(version)

      buildit(yawnie, requested[name], tmp, destination)

      # yawnie = yawn.Air(name)
      # tmp = FileSystem.join(config.get('temporary'), yawnie.get("master", "safename"))
      # destination = FileSystem.join(config.get('output'), yawnie.get("master", "safename"))
      # giti = yawnie.get('master', 'git')
      # # Get each version informations json
      # vinfos = {}
      # for version in requested[name]:
      #   vinfos[version] = yawnie.get(version)

      # build(giti, vinfos, tmp, destination)


      # y = yawn.Air(name)

      # for version in requested[name]:
      #   # category = y.get(version, 'category')
      #   tmp = FileSystem.join(config.get('temporary'), name, version)
      #   destination = FileSystem.join(config.get('output'), name, version)

      #   data = y.get(version)
      #   if ".travis.yml" in data:
      #     print "version %s is OK travis: %s" % (version, data[".travis.yml"])

        # print tmp, name, version, y.get(version, 'resources'), y.get(version, 'build'), y.get(version, 'productions'), destination, y.get(version, 'strict')
        # airb.buildone(tmp, name, version, y.get(version, 'resources'), y.get(version, 'build'),
        #     y.get(version, 'productions'), destination, y.get(version, 'strict'))



global buildit
def buildit(yawnie, versions, tmp, dest):

  # XXX horked if a specific version has a specific (different) git url

  nomasterhack = "master"
  try:
    yawnie.get('master', 'name')
  except:
    nomasterhack = yawnie.versions().pop()

  repomanager = gh.GitHelper(yawnie.get(nomasterhack, 'git'), tmp)
  repomanager.ensure()
  p = repomanager.getPath()
  white = ["build", "dist", "test", "tests"]

  for version in versions:
    print "Building version %s" % version

    tree = yawnie.get(version, "tree")

    repomanager.checkout(yawnie.get(version, "sha"))


    identified = False
    usenode = False

    trav = yawnie.get(version, ".travis.yml")
    if trav:
      if ("language" in trav) and (trav["language"] == "node_js"):
        usenode = identified = True
      else:
        print "DOESNT KNOW HOW TO BUILD CUSTOM TRAVIS SHIT"

    if yawnie.get(version, "devDependencies"):
      usenode = identified = True

    nob = yawnie.get(version, "nobuild")
    if nob:
      identified = True

    if not nob:
      usepuke = False
      if "pukefile.py" in tree:
        usepuke = identified = True

      usebundle = False
      if "Gemfile" in tree:
        usebundle = identified = True

      userake = False
      if "Rakefile" in tree:
        userake = identified = True

      usegrunt = False
      if "Gruntfile.js" in tree:
        usegrunt = identified = True

      useant = False
      if "build.xml" in tree:
        useant = identified = True

      usemake = False
      if "Makefile" in tree:
        usemake = identified = True

      if usenode:
        puke.sh('cd "%s"; npm install' % p)

      if usebundle:
        puke.sh('cd "%s"; bundle' % p, output = True)

      if usepuke:
        puke.sh('cd "%s"; puke all' % p, output = True)
      elif usegrunt:
        puke.sh('cd "%s"; grunt' % p, output = True)

      elif userake:
        puke.sh('cd "%s"; rake' % p, output = True)

      elif useant:
        puke.sh('cd "%s"; ant' % p, output = True)

      elif usemake:
        puke.sh('cd "%s"; make' % p, output = True)

      elif "build.sh" in tree:
        identified = True
        puke.sh('cd "%s"; ./build.sh' % p, output = True)

      # Yepnope...
      elif "compress" in tree:
        identified = True
        puke.sh('cd "%s"; ./compress' % p, output = True)

      # ES5...
      elif "minify" in tree:
        identified = True
        puke.sh('cd "%s"; ./minify' % p, output = True)

      if usenode:
        scripties = yawnie.get(version, "scripts")
        if scripties:
          for i in scripties:
            if i in white:
              puke.sh('cd "%s"; npm run-script %s' % (p, i))


    if not identified:
      raise "DONT KNOW WHAT TO DO"

    productions = yawnie.get(version, "productions")

    v = version.lstrip("v")
    destination = FileSystem.join(dest, v)
    if productions:
      for item in productions:
        local = FileSystem.realpath(FileSystem.join(p, productions[item]))
        if not FileSystem.exists(local):
          console.error("Missing production! %s (%s)" % (productions[item], local))
        else:
          if FileSystem.isfile(local):
            FileSystem.copyfile(local, FileSystem.join(destination, item))
          else:
            puke.deepcopy(puke.FileList(local), FileSystem.join(destination, item))



  nos = not yawnie.get(version, "nostrict")
  stuff = puke.FileList(dest, filter = "*.js", exclude = "*-min.js")
  puke.Tools.JS_COMPRESSOR = "%s.js.compress" % puke.sh("which puke", output = False).strip()
  for i in stuff.get():
    mined = re.sub(r"(.*).js$", r"\1-min.js", i)
    if not FileSystem.exists(mined):
      print "Missing minified version %s %s" % (i, mined)
      # XXX strict will blow here
      puke.minify(str(i), mined, strict = nos)


  # XXX too damn dangerous for the benefit - wontfix
  # puke.Tools.CSS_COMPRESSOR = "%s.css.compress" % puke.sh("which puke", output = False).strip()
  # stuff = puke.FileList(dest, filter = "*.css", exclude = "*-min.css")
  # for i in stuff.get():
  #   mined = re.sub(r"(.*).css$", r"\1-min.css", i)
  #   if not FileSystem.exists(mined):
  #     print "Missing minified version %s %s" % (i, mined)
  #     # XXX strict will blow here
  #     try:
  #       puke.minify(str(i), mined, strict = True)
  #     except:
  #       # Bootstrap fail on older versions
  #       print "FAILED COMPRESSION %s" % i






      # if local.split('.').pop().lower() == 'js':
      #   strict = True
      #   minify(str(local), re.sub(r"(.*).js$", r"\1-min.js", local), strict = strict)
      #   FileSystem.copyfile(re.sub(r"(.*).js$", r"\1-min.js", local), FileSystem.join(destination, re.sub(r"(.*).js$", r"\1-min.js", item)))



  # if productions:

  # else:


# @task("Get a specific info about a specific version of a library")
# def get(name, version, key):
#   a = yawn.Air(name)
#   print a.get(version, key)





# @task("Default task")
# def default():
#   print('Victory')
#   pass
  # executeTask("build")
  # executeTask("deploy")


# @task("All")
# def all():
#   executeTask("build")
#   executeTask("mint")
#   executeTask("deploy")
#   executeTask("stats")


# @task("Wash the taupe!")
# def clean():
#   PH.cleaner()

# # Get whatever has been built and exfilter some crappy stuff
# @task("Deploying")
# def deploy():
#   PH.deployer(False)


# @task("Stats report deploy")
# def stats():
#   PH.stater(Yak.build_root)


# @task("Minting")
# def mint():
#   # list = FileList(Yak.build_root, filter = "*bootstrap*.js", exclude = "*-min.js")
#   # for burne in list.get():
#   #   minify(burne, re.sub(r"(.*).js$", r"\1-min.js", burne), strict = False, ecma3 = True)
#   # raise "toto"
#   # These dont survive strict
#   PH.minter(Yak.build_root, filter = "*raphael*.js,*ember*.js,*yahoo*.js,*yepnope*.js,*modernizr*.js,*jasmine*.js", excluding=",*/jax*,*mathjax/fonts*", strict = False)
#   PH.minter(Yak.build_root, excluding = "*raphael*.js,*ember*.js,*yahoo*.js,*yepnope*.js,*modernizr*.js,*jasmine*.js,*/jax*,*mathjax/fonts*", strict = True)

# @task("Deploying the static ressources, including approved third party dependencies")
# def build(buildonly = False):
#   # Crossdomain
#   sed = Sed()
#   sed.add("<\!--.*-->\s*", "")
#   combine("src/crossdomain.xml", Yak.build_root + "/crossdomain.xml", replace = sed)

#   # Robots
#   sed = Sed()
#   # XXX partially fucked-up
#   sed.add("(?:^|\n+)(?:#[^\n]*\n*)+", "")
#   combine("src/robots.txt", Yak.build_root + "/robots.txt", replace = sed)

#   # Deepcopy other stuff
#   sed = Sed()
#   PH.replacer(sed)
#   list = FileList("src/", exclude="*robots.txt,*crossdomain.xml,*index.html")
#   deepcopy(list, Yak.build_root, replace=sed)


#   # Process the remote leaves
#   description = {}

#   # Yak.collection.items()
#   colls = PH.getyanks()
#   # print Yak.collection
#   # for name in Yak.collection:
#   #   print name
#   for name in colls:
#     packinfo = colls[name]
#     # Temporary and build output directories definitions
#     tmpdir = FileSystem.join(Yak.tmp_root, "lib", packinfo["Destination"], name)
#     builddir = FileSystem.join(Yak.build_root, "lib", packinfo["Destination"], name)

#     desclist = []
#     marker = 'lib/%s/' % packinfo["Destination"]
#     for(localname, url) in packinfo["Source"].items():
#       # Do the fetch of 
#       PH.fetchone(url, tmpdir, localname)
#       # Copy files that "exists" to build directory
#       f = FileSystem.join(tmpdir, localname)
#       if FileSystem.exists(f):
#         d = FileSystem.join(builddir, localname)
#         # if not FileSystem.exists(FileSystem.dirname(d)):
#         #   FileSystem.makedir(FileSystem.dirname(d));
#         FileSystem.copyfile(f, d)
#         # Augment desclist with provided localname
#         desclist += [FileSystem.join(marker, name, localname)]

#     if "Build" in packinfo:
#       buildinfo = packinfo["Build"]
#       production = buildinfo["production"]
#       tmpdir = FileSystem.join(tmpdir, buildinfo["dir"])
#       extra = ''
#       if 'args' in buildinfo:
#         extra = buildinfo["args"]
#       if not buildonly or buildonly == name:
#         PH.make(tmpdir, buildinfo["type"], extra)

#       # Copy production to build dir
#       for(local, builded) in production.items():
#         f = FileSystem.join(tmpdir, builded)
#         d = FileSystem.join(builddir, local)
#         desclist += [FileSystem.join(marker, name, local)]
#         if FileSystem.isfile(f):
#           FileSystem.copyfile(f, d)
#         elif FileSystem.isdir(f):
#           deepcopy(FileList(f), d)

#       # ["coin%s" % key for key in ['item1', 'item2']]


#       # map((lambda item: "%s%s" % (name, item)), ['item1', 'item2'])
#       # # Augment description list with build result
#       # bitch = production.keys();

#       # for x in bitch:
#       #   bitch[x] = FileSystem.join(name, bitch[x]);

#       # print bitch
#       # raise "toto"

#       # desclist = desclist + production.keys()

#     description[name] = desclist
#     # description[name] = "%s%s" % (name, marker, ('",\n"%s' % marker).join(desclist)))

#     # miam += """
#     #   %s:
#     #     ["%s%s"]
#     # """ % (name, marker, ('", "%s' % marker).join(desclist))
#   # FileSystem.writefile(FileSystem.join(Yak.build_root, "airstrip.yaml"), yaml.dump(yaml.load('\n'.join(description))))


#     # print json.dumps(description)
#     # raise "toto"

#   shortversion = Yak.package['version'].split('-').pop(0).split('.')
#   shortversion = shortversion[0] + "." + shortversion[1]
#   PH.describe(shortversion, "airstrip", description)
#   # Write description file
#   # FileSystem.writefile(FileSystem.join(Yak.build_root, "airstrip.json"), '{%s}' % ',\n'.join(description))

#   # Build-up the description file
#   file = "src/index.html"
#   sed.add("{PUKE-LIST}", json.dumps(description, indent=4))
#   deepcopy(file, Yak.build_root, replace=sed)


