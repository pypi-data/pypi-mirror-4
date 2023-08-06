import json
import os
from functools import partial

from dateutil.parser import parse as parse_date

import gevent


import mechanize
import requests
import websocket

INFINITY = float('inf')

class Client(object):
  def __init__(self, host, auth_input, port=80, cookie_path="cookie3.txt"):
    self.host = host
    self.port = port
    self.auth_input = auth_input
    self.cookie_path = cookie_path
        
    self.br = mechanize.Browser()
    self.br.set_handle_robots(False)
    
    cj = self.cookiejar = mechanize.LWPCookieJar()
    if os.path.exists(cookie_path):
      cj.load(cookie_path)

    self.br.set_cookiejar(cj)
    self.login()
    assert self.br.geturl().endswith('integrated')
    cj.save(cookie_path)


  @property
  def base_url(self):
    return "http://{host}:{port}".format(
      host = self.host,
      port = self.port
    )

  def get(self, relative_url, *args, **kw):
    return requests.get(self.base_url + relative_url, cookies=self.cookies, *args, **kw)
    
  def post(self, relative_url, data=None):
    return requests.post(self.base_url + relative_url, data, cookies=self.cookies)

    
  @property
  def cookies(self):
    cookies = {}
    for cookie in self.cookiejar:
      if cookie.domain == self.host:
        cookies[cookie.name] = cookie.value
    return cookies

  def projects(self):
    resp = self.get("/workspaces/")
    resp.raise_for_status()
    projects = resp.json()

    return map(lambda d: Project(session=self, **d), projects)
    
  def login(self):
    br = self.br

    br.open(self.base_url)

    if not br.geturl().endswith('integrated'):
      # login with github
      response = br.follow_link()

      if br.geturl().endswith('integrated'):
        # github redirected us back, we're good to go
        return
      else:
        br.select_form(nr=0)
        br['login'], br['password']  = self.auth_input()
        br.submit()
      
  def create_project(self, **kw):
    resp = self.post("/workspaces", kw)
    return resp.content
    
  def rebuild(self, project_id, keep):
    if keep:
      keep = '?keep=true'
    else:
      keep = ''
    self.post("/workspaces/{}/rebuild{}".format(project_id, keep))
    
  def rebuild_segment(self, project_id, table, segment):
    self.post("/workspaces/{}/{}/{}/rebuild".format(project_id, table, segment))



class Project(object):
  def __init__(self, **kw):
    self.set_attrs(kw)
    
  def set_attrs(self, dict):
    for key,value in dict.items():
      setattr(self, key, value)
      
  def __repr__(self):
    return "Project: {}  queued: {} failed: {} built: {}".format(
      self.title,
      len(self.queued),
      len(self.failed),
      len(self.built),
      
    )

  @property
  def segments(self):
    collection = []

    for table in self.tables.values():
      collection.extend(table['segments'])
    return collection

  def filter(self, status):
    return [s for s in self.segments if s['status'] == status]
  
  @property
  def built(self):
    return self.filter('built')
  
  @property
  def building(self):
    # todo: have server return building
    return []
    
  @property
  def queued(self):
    return self.filter('pending')
  
  @property  
  def failed(self):
    return self.filter('failed')


  def next_build_in(self):
    # returns the number of seconds until the next build or INFINITY
    # if the project well never be built (errors, paused, etc)

    if hasattr(self, 'next_build_at') and self.next_build_at is not None:
      interval = parse_date(self.next_build_at) - parse_date(self.current_date_time)
      return interval.total_seconds()
    else:
      return INFINITY
  
  def query(self, query, **headers):
    return self.session.get(
      '/workspaces/{}/query'.format(self.id), 
      params={'q': query},
      headers=headers,
      stream=True
    )
    
    
  def resume(self):
    return self.session.post(
      '/workspaces/{}/resume'.format(self.id)
    )
    

  def simulate(self, target, **headers):
    return self.session.get(
      '/workspaces/{}/simulate/{}'.format(self.id, target),
      headers=headers,
      stream=True
    )
    
  def step(self, target):
    return self.session.post(
      '/workspaces/{}/step/{}'.format(self.id, target),
    )
  
    
        
  def import_repo(self, url, owner, name, branch='master'):

    return self.session.post(
      '/workspaces/{}/import_repo'.format(self.id),
      {
        'url':    url,
        'owner':  owner,
        'name':   name,
        'branch': branch
      }
    )
    


  @property
  def repositories(self):
    return self.session.get('/workspaces/{}/repos'.format(self.id)).json()
      
  def subscribe(self, callback):

    def on_open(socket, *args, **kw):
      gevent.spawn(ping, socket)
      socket.send("1::/"+self.id)

    def on_message(socket, msg, *args, **kw):
      code, data, namespace, payload = msg.split(':',3)
      code = int(code)
      if code == 1:
        gevent.spawn(callback,self, {})
      elif code == 5:
        event = json.loads(payload)
        gevent.spawn(callback, self, *event['args'])

    def on_error(socket, msg, *args, **kw):
      print 'error', msg, args, kw
      
    hand_shake_url ='/socket.io/1/'
    #resp = requests.get(hand_shake_url, cookies=c)

    resp = self.session.post(hand_shake_url)

    sid,heartbeat_timeout,connection_timeout,accetped = resp.content.split(':')
    sid,heartbeat_timeout,connection_timeout = map(int, (
      sid,heartbeat_timeout,connection_timeout
    ))
    
    ws_url = 'ws://{}:{}/socket.io/1/websocket/{}'.format(
      self.session.host,
      self.session.port,
      sid
    )
    
    def ping(socket):
      timeout = max(heartbeat_timeout - 1, 1)
      while socket.sock.connected:
        socket.send("2::")
        gevent.sleep(timeout)
    
    
    headers = ['Cookie: %s' % resp.request.headers['Cookie']]
    #from gevent import monkey; monkey.patch_all()
    ws = websocket.WebSocketApp(
      ws_url,
      header=headers,
      on_open   =on_open,
      on_message = on_message,
      on_error = on_error
    )

    ws.run_forever()
  
  
