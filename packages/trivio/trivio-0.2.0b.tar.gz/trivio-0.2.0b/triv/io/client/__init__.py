#!/usr/bin/env python

import json
import os
import sys
import re
import time
from urlparse import urlparse

import api

import gevent


INFINITY = float('inf')


PROJECT_FILE='.trivio.project'

COOKIE_JAR_PATH="cookie3.txt"
PARSE_GITHUB_URL=re.compile('git@github.com:(\w+)/(\w+).git')


default_url="http://app.triv.io:80"

def auth_input():
  login = raw_input('login: ')
  password = raw_input('password: ')
  return login, password

def format_delay(seconds):
  if seconds == INFINITY:
    return "forever"
  
  seconds = int(seconds)
  minutes = 60
  hours   = minutes * 60
  days    = hours * 24
  
  t = []
  for label, part in [('d', days), ('h',hours), ('m',minutes)]:
    whole, seconds = divmod(seconds, part)
    if whole == 0 and len(t) == 0:
      continue
    else:
      t.append("{:02d}{}".format(whole,label))
  t.append("{:02d}{}".format(seconds,'s'))

    
  return " ".join(t)

def rules_view(project):
  row_format = "{:40} {:>8} {:>8} {:>8} {:>8}"
  
  # generates one empty string per field applies it to the
  # format and measures the length of the string
  row_length = len(row_format.format(*(['']*5)))
  
  clearline()
  print row_format.format("", "Queued", "Building","Failed", "Built")
  
  print '-' * row_length
  
  print row_format.format(
    "All", 
    len(project.queued),
    len(project.building),
    len(project.failed),
    len(project.built)
  )
  line_count = 3

  for title, table in project.tables.items():
    #title = rule['target']
    #table = project.tables[title]
    
    if(len(title) > 40):
      title = '...' + title[-37:]
      
    counts = {}
    for segment in table['segments']:
      status = segment['status']
      counts[status] = counts.get(status,0) + 1
  
    print row_format.format(
      title,
      counts.get('queued', 0),
      counts.get('building', 0),
      counts.get('failed', 0),
      counts.get('built', 0)
    )
    line_count += 1
  
  return line_count
    
  

def clearline(s=''):
  sys.stdout.write("\r\x1b[K" + s)
  sys.stdout.flush()

def moveup(n=1):
  sys.stdout.write("\r\033[{:d}A".format(n))
  sys.stdout.flush()


def current_project(session):
  """
  
  Returns the current project or None if the trivio command was run from
  outside a trivio project directory..
  
  This method searches the current directory for a file named ".trivio.project"
  if it can't be found it will search each ancestor directory.
  """
  path = os.getcwd()
  
  while path != '/':
    try:
      project_props = json.load(open(os.path.join(path, PROJECT_FILE)))
      print "Changing to dir " + path
      os.chdir(path)
      return api.Project(session=session, **project_props)
    except IOError:
      path = os.path.dirname(path)

def current_target(settings_path):
  settings = None

  if os.path.exists(settings_path):
    content = open(settings_path).read()
    if content:
      settings = json.loads(content)
    else:
      settings = None

  if settings is None:
    settings = target_cmd(settings_path)
    
  return settings['target_url']

def create_cmd(client, title, *repos):
  """
  Creates a new project, ensuring the user is not under a project directory first.
  """
  assert current_project(client) is None
  
  print "Creating project directory"
  os.mkdir(title)
  print "Creating repositories"
  os.mkdir(os.path.join(title, "repositories"))
  
  
  print "Creating trivio project"
  project = client.create_project(title=title)
  open(os.path.join(title, PROJECT_FILE), 'w').write(project)


def checkout_cmd(client, title_or_id=None):
  assert current_project(client) is None
  if title_or_id is None:
    available=client.projects()
  else:

    available = []
    for project in client.projects():
      if (project.title and project.title.startswith(title_or_id))  or project.id.startswith(title_or_id):
        available.append(project)
        
  if len(available) == 1:
    project = available[0]
  else:
    # to many projects match, prompt the user
    print "Which project would you like to work on?"
    for i, project in enumerate(available):
      print i,' ', project
    
    index = int(raw_input("Enter number of projct to workon: "))
    project = available[index]


  if os.path.exists(project.title):
    print "Project {} already exists".format(project.title)
  else:    
    os.mkdir(project.title)
    os.chdir(project.title)
    open(PROJECT_FILE, 'w').write(json.dumps(
      dict(
        id=project.id,
        title=project.title
      )
    ))
    
    os.mkdir('repositories')
    os.chdir('repositories')
    return pull_cmd(client)

def import_cmd(client, git_url):
  project = current_project(client)
  
  owner, repo = PARSE_GITHUB_URL.search(git_url).groups()
  
  repo = repo.split('.git')[0]

  resp = project.import_repo(git_url, owner, repo)
  pull_cmd(client)

def remove_repo_cmd(client, path):
  project = current_project(client)
  print path

def errors_cmd(client, project_id=None):
  project = current_project(client)
  print project.rule_errors, project.rules
  for error in project.rule_errors:
    print error
    
def remove_cmd(client, project_id=None):
  """
  Removes the idetified project, if no project was specified prompts the user
  to select the project to remove.
  """
  if project_id is None:
    projects = client.projects()

    for i, p in enumerate(projects):
      print "  {}: {.title}".format(i,p)
    x = int(raw_input("Enter project to remove: "))
    project_id = projects[i].id
  print "removing " + project_id
    
def target_cmd(settings_path, target_url=None):
  if target_url is None:
    target_url = raw_input("Enter URL [{}]:".format(default_url))
    if target_url.strip() == '':
      target_url = default_url
      
  settings = dict(target_url=target_url)
  open(settings_path, 'w').write(json.dumps(settings))
  return settings
 
def list_cmd(client):
  """Print a list of each project for the logged in user."""

  for project in client.projects():
    print project
    
    
def pull_cmd(client):
  """Updates the repos in the project directory to match the project on trivio"""
  
  project = current_project(client)
  os.chdir('repositories')
  
  for repo in  project.repositories:
    if not os.path.exists(repo['owner']):
      os.mkdir(repo['owner'])
    os.chdir(repo['owner'])
    if not os.path.exists(repo['name']):
      print "Cloning " + repo['name']
      os.system('git clone ' + repo['git_url'])
    else:
      print "Updating " + repo['name']      
      os.chdir(repo['name'])
      os.system('git pull')
      os.chdir('..')
    os.chdir('..')
      

 
def push_cmd(client, msg="pushing", keep=False):
  
  """
  Rebuilds the project after commiting and pushing changes for any modified
  repository.
  """

  if isinstance(keep, basestring):
    keep = keep.lower().strip()
    if keep == 'true':
      keep = True
    elif keep == 'false':
      keep = False
    else:
      raise ValueError('invalid value "{}"'.format(keep))

  project = current_project(client)
  # getting the current project should put us in the correct directory  

  curdir = os.getcwd()
  os.chdir('repositories')
  for owner in os.listdir('.'):
    print "changing to " + owner
    os.chdir(owner)
    for repo in os.listdir('.'):
      os.chdir(repo)
      os.system('git commit -am "{}"; git push'.format(msg))
      os.chdir('..')
    os.chdir('..')
  client.rebuild(project.id, keep)

def rebuild_cmd(client, table=None, segment=None):
  project = current_project(client)
  if (table, segment) == (None, None):
    client.rebuild(project.id, keep=False) 
  else:
    client.rebuild_segment(project.id, table, segment) 

    
   
def query_cmd(client, query_str, accept="application/x-json-stream"):
  print query_str
  project = current_project(client)

  for chunk in project.query(query_str, accept=accept).iter_content(chunk_size=10240):
    sys.stdout.write(chunk)

def resume_cmd(client):
  project = current_project(client)
  print project.resume().content
  

def watch_cmd(client):
  project = current_project(client)
  from gevent import monkey; monkey.patch_all(thread=False)
  gevent.spawn(project.subscribe,on_project_update).join()
  
def on_project_update(project, attrs):
  project.set_attrs(attrs)
  print project
  line_count = rules_view(project)
  
  seconds = project.next_build_in()
  while seconds > 0:
    time.sleep(1)
    seconds -= 1

    clearline(
      "Next build in {} seconds".format(format_delay(seconds))
    )
  print
  
  
  
def simulate_cmd(client, target, accept='application/x-json-stream'):
  project = current_project(client)
  for chunk in project.simulate(target, accept=accept).iter_content(chunk_size=10240):
    sys.stdout.write(chunk)

def step_cmd(client, target):
  project = current_project(client)
  print project.step(target).content


def main():
  args = sys.argv[1:]
  command = args[0]
  
  # setup cookie dir
  trivio_dir = os.path.expanduser('~/.triv.io')
  if not os.path.exists(trivio_dir):
    os.mkdir(trivio_dir)

  settings_path = os.path.join(trivio_dir, 'settings.json')

  if command == 'target':
    target_cmd(settings_path)
    sys.exit(0)
  else:
    target_url =  current_target(settings_path)
  
  url = urlparse(target_url)
  
  client = api.Client(
    url.hostname,
    auth_input,
    port=url.port,
    cookie_path = os.path.join(trivio_dir, 'cookies.txt')
  )    
  
  method = globals().get(command+'_cmd', None)
  if method is None:
    method = query_cmd
  else:
    args.pop(0)
    

  try:
    try:
      method(client, *args)
    except KeyboardInterrupt:
      pass
  finally:
    print
    


  
if __name__ == "__main__":
  main()
