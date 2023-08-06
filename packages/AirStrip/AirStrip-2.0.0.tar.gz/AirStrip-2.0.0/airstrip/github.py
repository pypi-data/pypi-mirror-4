from puke import *
import puke.Cache
import json
import yaml
import os
import base64
import requests
import sys, logging, os, traceback


GITHUB_ROOT = "https://api.github.com"
GITGIT_ROOT = "https://github.com"
GITRAW_ROOT = "https://raw.github.com"

class GitHubInit():
  ########################################
  # HTTP
  ########################################
  def __simpleGet__(self, url):
    print " [http] simple get %s" % url
    r = requests.get(url)
    return r.text or r.content

  def __cachedGet__(self, u):
    print " [http] cached get %s" % u
    id = puke.Cache.fetchHttp(u).split('/').pop()
    return puke.Cache.read(id)

  ########################################
  # Github tokens
  ########################################

  def __getToken__(self):
    print " [github-token] searching for existing auth token"

    d = requests.get("%s/authorizations" % GITHUB_ROOT, auth = self.auth)
    r = json.loads(d.text or d.content)
    for i in r:
      if i["note"] == "airstrip":
        print " [github-token] found existing auth token %s" % i["token"]
        return i["token"]
    return False

  def __destroyTokens__(self):
    print " [github-token] destroying auth tokens"

    d = requests.get("%s/authorizations" % GITHUB_ROOT, auth = self.auth)
    r = json.loads(d.text or d.content)
    for i in r:
      if i["note"] == "airstrip":
        e = requests.delete("%s/authorizations/%s" % (GITHUB_ROOT, i["id"]), auth = self.auth)

  def __createToken__(self):
    print " [github-token] creating new auth token"

    payload = {"scopes": ["public_repo"], "note": "airstrip"}
    headers = {'content-type': 'application/json'}
    d = requests.post("%s/authorizations" % GITHUB_ROOT, data=json.dumps(payload), headers=headers, auth = self.auth)
    r = json.loads(d.text or d.content)
    return r["token"]





  def apiGet(self, fragment):
    u = "%s/%s?access_token=%s" % (GITHUB_ROOT, fragment, self.token)
    r = self.__simpleGet__(u)
    try:
      return json.loads(r)
    except Exception as e:
      console.fail(" [github-connector] Failed json-interpreting url %s with payload %s" % (u, r))

  def apiCacheGet(self, fragment):
    print " [github-connector] cache fetching %s" % fragment
    u = "%s/%s?access_token=%s" % (GITHUB_ROOT, fragment, self.token)
    r = self.__cachedGet__(u)
    try:
      return json.loads(r)
    except Exception as e:
      console.fail(" [github-connector] Failed json-interpreting cached url %s with payload %s" % (u, r))



  # def buildUrl(self, fragment):
  #   return "%s/%s?access_token=%s" % (GITHUB_ROOT, fragment, self.token)

  def __init__(self):
    consoleCfg = logging.StreamHandler()
    consoleCfg.setFormatter(logging.Formatter( ' %(message)s' , '%H:%M:%S'))
    logging.getLogger().addHandler(consoleCfg)
    logging.getLogger().setLevel(logging.DEBUG)

    self.uname = prompt("Github username")
    self.pwd = prompt("Github password")

    self.auth = requests.auth.HTTPBasicAuth(self.uname, self.pwd)

    token = self.__getToken__()
    # self.destroyTokens()
    if not token:
      token = self.__createToken__()

    self.token = token

  def retrieve(self, owner, repo, dest, name):
    print " [github-connector] working on %s/%s" % (owner, repo)

    # Get refs for a starter
    refs = self.apiGet("repos/%s/%s/git/refs" % (owner, repo))

    print " [github-connector] found %s refs" % len(refs)

    tags = {}
    # Get and init every tag, plus master
    for i in refs:
      tag = i["ref"].split('/').pop()
      if i["ref"].startswith("refs/tags/") or i["ref"].startswith("refs/heads/master"):
        tags[tag] = {"sha": i["object"]["sha"]}
        tags[tag]["tree"] = {}
        tags[tag]["package.json"] = {
          "name": repo,
          "author": owner,
          "version": tag
        }

    print " [github-connector] found %s tags" % len(tags)

    for tag in tags:
      sha = tags[tag]["sha"]
      print " [github-connector] analyzing tag %s (sha %s)" % (tag, sha)

      if tag == "master":
        tree = self.apiGet("repos/%s/%s/git/trees/%s" % (owner, repo, sha))
      else:
        tree = self.apiCacheGet("repos/%s/%s/git/trees/%s" % (owner, repo, sha))

      date = self.apiCacheGet("repos/%s/%s/git/commits/%s" % (owner, repo, sha))
      try:
        tags[tag]["date"] = {
          "authored": date["author"]["date"],
          "commited": date["committer"]["date"]
        }
      except:
        tags[tag]["date"] = {
          "authored": False,
          "commited": False
        }
        print sha
        console.error('Failed fetching a commit!!!')

      for item in tree["tree"]:
        if item["path"].lower() in ['package.json', 'component.json', '.travis.yml']:
          print " [github-connector] actually reading file %s" % item["path"]
          # XXX avoid API call
          item["url"] = "%s/%s/%s/%s/%s" % (GITRAW_ROOT, owner, repo, tag, item["path"].lower())

          if tag == "master":
            d = self.__simpleGet__(item["url"])
          else:
            d = self.__cachedGet__(item["url"])
          try:
            tags[tag][item["path"].lower()] = json.loads(d)
          except:
            try:
              tags[tag][item["path"].lower()] = yaml.load(d)
            except:
              pass
        elif "url" in item:
          tags[tag]["tree"][item["path"]] = item["url"]

    previous = {}
    p = FileSystem.join(dest, '%s.json' % name)
    if FileSystem.exists(p):
      previous = json.loads(FileSystem.readfile(p))

    previous["versions"] = tags
    previous["git"] = "%s/%s/%s" % (GITGIT_ROOT, owner, repo)

    FileSystem.writefile(p, json.dumps(previous, indent=4))



# g = GitHubInit()
# # g.retrieve("documentcloud", "backbone", "airstrip/airs", "backbone")
# # g.retrieve("twitter", "bootstrap", "airstrip/airs", "bootstrap")
# g.retrieve("emberjs", "ember.js", "airstrip/airs", "ember")
# g.retrieve("h5bp", "html5-boilerplate", "airstrip/airs", "h5bp")
# g.retrieve("wycats", "handlebars.js", "airstrip/airs", "handlebars")
# # g.retrieve("jquery", "jquery", "airstrip/airs", "jquery")
# g.retrieve("necolas", "normalize.css", "airstrip/airs", "normalize")
# # g.retrieve("madrobby", "zepto", "airstrip/airs", "zepto")







  # @staticmethod
  # def getblob(url, tmp):
  #   deepcopy(FileList(url), tmp)
  #   content = json.loads(FileSystem.readfile(FileSystem.join(tmp, url.split('/').pop())))
  #   return base64.b64decode(content["content"])

  # @staticmethod
  # def getraw(url, tmp):
  #   deepcopy(FileList(url), tmp)
  #   return FileSystem.readfile(FileSystem.join(tmp, url.split('/').pop()))


# /repos/:owner/:repo/git/trees/:sha

# 4a95dae0378f6e3058f70c51bff03318fb5fc63a






  # config = airc.AirConfig()
  # config.get('temporary')