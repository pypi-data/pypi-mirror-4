import os
import sys

from configobj import ConfigObj

def get_server_config():
  config = ConfigObj(os.path.expanduser('~/.workbox'))
  servers = []
  for server_name in config:
    server = config.get(server_name)
    servers.append({
        'name': server_name,
        'base_url': server.get('base_url'),
        'username': server.get('username'),
        'password': server.get('password')})

  return servers

def p(s, args=(), out=sys.stdout):
  print >> out, "\n  " + s % args

def expand_range(r):
  def expand(s):
    try:
      return [int(s)]
    except ValueError, e:
      if '-' in s:
        try:
          low, high = s.split('-')
          return range(int(low), int(high)+1)
        except ValueError, e:
          raise Exception, "Invalid range specified."
      else:
        raise Exception, "Unrecognisable range value specified."

  return sum([expand(p) for p in r.split(',')], [])

if __name__ == '__main__':
  print expand_range('1-3')
  print expand_range('1')
  print expand_range('1,2')
  print expand_range('1,2,3-5,6')
