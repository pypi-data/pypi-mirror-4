import requests
import json
import os.path
import sys
from utils import get_server_config, p

class ConfluenceServer(object):
  def __init__(self, name, base_url, auth):
    self.name = name
    self.base_url = os.path.join(base_url, 'rest/mywork/latest/task')
    self.auth = auth

  def _req(self, method, url, data={}, json_response=True):
    req = getattr(requests, method)(url, data=json.dumps(data), auth=self.auth,
        headers={'content-type': 'application/json'})

    if req.status_code == 200:
      if json_response:
        try:
          return json.loads(req.content)
        except:
          p("Couldn't process Confluence's response.\n", out=sys.stderr)
          sys.exit(1)
      else:
        return req
    elif req.status_code == 401:
      p("Bad username/password.\n", out=sys.stderr)
      sys.exit(1)
    elif req.status_code == 500:
      p("Confluence encountered an error.\n", out=sys.stderr)
      sys.exit(1)
    else:
      p("Encountered an unknown error.\n")
      sys.exit(1)

  def get_tasks(self):
    tasks = self._req('get', self.base_url)
    
    if not tasks:
      return []

    todo = []
    for task in tasks:
      if task['status'] == 'TODO':
        task['server'] = self
        todo.append(task)

    return todo

  def add_task(self, text):
    return self._req('post', self.base_url, {
        'title': text, 
        'status': 'TODO',
        'application': 'com.atlassian.workbox-cli'
      })

  def complete_task(self, task_id):
    return self._req('put', '%s/%d' % (self.base_url, task_id), {
        'status': 'DONE'
      })

  def _set_position(self, task_id, before_task_id):
    return self._req('put', '%s/%d/position' % (self.base_url, task_id), {
      'before': before_task_id}, json_response=False)

  def float_task(self, task_id, first_task_id):
    return self._set_position(task_id, first_task_id)

  def sink_task(self, task_id):
    return self._set_position(task_id, None)

  def remove_task(self, task_id):
    return self._req('delete', "%s/%d" % (self.base_url, task_id), json_response=False)

def load_servers():
  server_config = get_server_config()
  if not server_config:
    print >> sys.stderr, "\n  You need to configure some Confluence servers. Try `workbox config` for some help.\n"
    sys.exit(1)

  return [ConfluenceServer(s['name'], s['base_url'], (s['username'], s['password'])) for s in server_config]

def get_tasks():
  federated_tasks = []
  for server in load_servers():
    federated_tasks += server.get_tasks()

  return federated_tasks

def add_task(title):
  return load_servers()[0].add_task(title)

