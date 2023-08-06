# -*- coding: utf8 -*-

from puke import *
import json
import os
import datetime
import re

import airrc
import airlicenses

# import airrc

AIRSTRIP_ROOT = os.path.dirname(os.path.realpath(__file__))

class Seeder():
  def __init__(self):
    pass

  def project(self):
    self.rc = airrc.AirRC()


    console.info("""This will seed a project in the current working directory.
You can leave any of the following informations blank, or later edit the generated files to fit your mileage.""")

    # Existing git repo
    std = Std()
    gitdata = sh('git remote -v', std = std)
    if not std.err:
      gitdata = gitdata.split('\n')
      gitdata.pop()
      gitdata = gitdata.pop().split(' ')
      gitdata.pop()
      gitdata = gitdata.pop().split('\t')
      gitdata = gitdata.pop().split('/')

      clean = re.sub('[.]git$', '', gitdata.pop())
      gitdata = {'repo': clean, 'owner': gitdata.pop().split(':').pop()}
    else:
      console.error('Current directory is not a git repository. Git data will be missing.')
      gitdata = False

    # User-provided informations
    defaultname = FileSystem.basename(FileSystem.realpath('.'))
    name = prompt("Pick a fancy project name (default %s)" % defaultname, defaultname).strip()
    description = prompt("Short description for your project").strip()
    k = prompt("Keywords for your project (comma separated)").strip().split(',')
    keywords = []
    for i in k:
      i = i.lower().strip()
      if i:
        keywords.append(i)
    keywords = json.dumps(keywords)


    # Default suggestions?
    yes = prompt("""Other informations can be automatically populated from your defaults (.airstriprc).
Would you like that (default, "y"), or would you prefer to review them one by one ("N")?""", "y")

    if not self.rc.get('you')['name']:
      self.rc.get('you')['name'] = Env.get("PUKE_LOGIN", System.LOGIN)

    you = self.rc.get('you').copy()
    company = self.rc.get('company').copy()
    homepage = company['url']
    license = self.rc.get('license')
    ln = self.rc.get('ln')
    git = self.rc.get('git')

    airl = airlicenses.AirLicenses()
    if yes.lower() == 'y':
      if not gitdata:
        gitdata = {'repo': git, 'owner': defaultname}
    else:
      company["name"] = prompt("The author name of the project and copyright owner (default: %s)" % company["name"], company["name"]).strip()
      company["mail"] = prompt("Author email (default: %s)" % company["mail"], company["mail"]).strip()
      company["url"] = prompt("Author url (default: %s)" % company["url"], company["url"]).strip()

      you["name"] = prompt("The principal package maintainer name of the project (default: %s)" % you["name"], you["name"]).strip()
      you["mail"] = prompt("Maintainer email (default: %s)" % you["mail"], you["mail"]).strip()
      you["url"] = prompt("Maintainer url (default: %s)" % you["url"], you["url"]).strip()

      keys = airl.list()
      seg = prompt("License for your project (choose from: %s, default: %s)" % (keys, license or 'MIT'), license or 'MIT').strip().upper()
      if not seg in keys:
        seg = license or 'MIT'
        console.error('Unknown license, fallbacking to %s' % seg)
      license = seg


      seg = prompt("License for your project (choose from: %s, default: %s)" % (keys, license or 'MIT'), license or 'MIT').strip().upper()
      ln = prompt("Language for your project (default: %s)" % ln, ln).strip()

      homepage = prompt("Homepage for your project? (default: %s)" % homepage, homepage).strip()

      if not gitdata:
        gitdata = prompt("Github owner/repositoryname (default: %s/%s)" % (git, defaultname), "%s/%s" % (git, defaultname)).strip()
        if gitdata:
          gitdata = gitdata.split('/')
          gitdata = {'repo': gitdata.pop(), 'owner': gitdata.pop()}
        else:
          gitdata = False

    # Preparing replacement patterns from provided information
    s = Sed()
    s.add('{{miniboot.name}}', name)
    s.add('{{miniboot.ln}}', ln)
    s.add('{{miniboot.description}}', description)
    s.add('{{miniboot.keywords}}', keywords)
    s.add('{{miniboot.homepage}}', homepage)

    s.add('{{miniboot.you.name}}', you['name'])
    s.add('{{miniboot.you.mail}}', you['mail'])
    s.add('{{miniboot.you.web}}', you['url'])
    s.add('{{miniboot.company.name}}', company['name'])
    s.add('{{miniboot.company.mail}}', company['mail'])
    s.add('{{miniboot.company.web}}', company['url'])

    now = datetime.datetime.now()
    s.add('{{miniboot.year}}', str(now.year))

    s.add('{{miniboot.path}}', FileSystem.realpath('.'))

    track = ''
    rep = ''
    if gitdata:
      track = 'https://github.com/%s/%s/issues' % (gitdata["owner"], gitdata["repo"])
      rep = 'https://github.com/%s/%s.git' % (gitdata["owner"], gitdata["repo"])

    s.add('{{miniboot.tracker}}', track)
    s.add('{{miniboot.repository}}', rep)

    lurl = airl.get(license)['url']
    lname = license

    s.add('{{miniboot.license.name}}', lname)
    s.add('{{miniboot.license.url}}', lurl)

    items = FileList(FileSystem.join(AIRSTRIP_ROOT, 'boilerplates'))
    deepcopy(items, '.', replace = s)

    d = FileSystem.readfile('LICENSE.md')
    FileSystem.writefile('LICENSE.md', '%s\n\n%s' % (d, airl.get(license)['content']))

    FileSystem.writefile('package-%s-%s.json' % (System.LOGIN, System.OS.lower()), '{}')
    deepcopy(FileList(FileSystem.join(AIRSTRIP_ROOT, 'boilerplates', 'src')), './src', replace = s)


