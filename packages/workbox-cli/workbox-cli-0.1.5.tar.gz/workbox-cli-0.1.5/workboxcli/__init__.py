import rest
from utils import p, expand_range

import random
import argparse

def render_task(i, task):
  return "  [%s] [%d] %s" % (task['server'].name, i, task['title'])

def render_tasks(tasks):
  if not tasks:
    return "\n  You have nothing to do. Beer!\n"

  task_output = []
  for i, task in enumerate(tasks):
    task_output.append(render_task(i, task))

  return "\n" + "\n".join(task_output) + "\n"

def list_tasks():
  task_data = rest.get_tasks()
  print render_tasks(task_data)

def add_task(titles):
  for title in titles:
    task = rest.add_task(title)
    p("Created task '%s' with ID #%s.", (task['title'], task['id']))

  list_tasks()

complete_messages = ["KAPOW", "SHAZAM", "ZORK", "POW", "CLANG", "ZAP", "THWAP", "ZORK"]

def complete_task(task_data, index):
  try:
    task_id = task_data[index]['id']
    task = task_data[index]['server'].complete_task(task_id)
    if task:
      p("Completed task with ID #%s. %s!", (task['id'], random.choice(complete_messages)))
      return True
    else:
      p("Failed to complete task.")
      return False
  except IndexError, e:
    p("Invalid index specified.\n")
    return False

def complete_tasks(index_range):
  task_data = rest.get_tasks()
  completed = []

  for index in expand_range(index_range):
    if complete_task(task_data, index):
      completed.append(index)
  
  print render_tasks([td for (i, td) in enumerate(task_data) if i not in completed])

def remove_task(task_data, index):
  try:
    task_id = task_data[index]['id']
    removed = task_data[index]['server'].remove_task(task_id)
    if removed:
      p("Deleted task with ID #%s.", (task_id,))
      return True
    else:
      p("Failed to remove task.")
      return False
  except IndexError, e:
    p("Invalid index specified.\n")
    return False

def remove_tasks(index_range):
  task_data = rest.get_tasks()
  removed = []

  for index in expand_range(index_range):
    if remove_task(task_data, index):
      removed.append(index)

  print render_tasks([td for (i, td) in enumerate(task_data) if i not in removed])

def float_task(index):
  task_data = rest.get_tasks()
  try:
    task_id = task_data[index]['id']
    floated = task_data[index]['server'].float_task(task_id, task_data[0]['id'])
    if floated:
      p("Floated task with ID #%s to the top.", (task_id,))
      list_tasks()
      return True
    else:
      p("Failed to float task.")
      list_tasks()
      return False
  except IndexError, e:
    p("Invalid index specified.\n")
    return False

def sink_task(index):
  task_data = rest.get_tasks()
  try:
    task_id = task_data[index]['id']
    sunk = task_data[index]['server'].sink_task(task_id)
    if sunk:
      p("Sunk task with ID #%s to the bottom.", (task_id,))
      list_tasks()
      return True
    else:
      p("Failed to sink task.")
      list_tasks()
      return False
  except IndexError, e:
    p("Invalid index specified.\n")
    return False

def main():
  parser = argparse.ArgumentParser(description='Confluence WorkBox CLI')
  sub_parsers = parser.add_subparsers()

  list_parser = sub_parsers.add_parser('list', help='List your tasks')
  list_parser.set_defaults(cmd='list', help='List your tasks')
  
  add_parser = sub_parsers.add_parser('add', help='Add a task')
  add_parser.add_argument('titles', nargs='*', help='1 or more task titles')
  add_parser.set_defaults(cmd='add')

  complete_parser = sub_parsers.add_parser('complete', help='Complete a task')
  complete_parser.add_argument('index_range', help='Indexes to complete. Can be comma separated and use ranges (e.g. 3-5)')
  complete_parser.set_defaults(cmd='complete')

  sink_parser = sub_parsers.add_parser('sink', help='Sink a task to the bottom.')
  sink_parser.add_argument('index', help='Index of task to sink.')
  sink_parser.set_defaults(cmd='sink')

  float_parser = sub_parsers.add_parser('float', help='Float a task to the top.')
  float_parser.add_argument('index', help='Index of task to float.')
  float_parser.set_defaults(cmd='float')

  remove_parser = sub_parsers.add_parser('rm', help='Remove a task')
  remove_parser.add_argument('index_range', help='Indexes to remove. Can be comma separated and use ranges (e.g. 3-5)')
  remove_parser.set_defaults(cmd='remove')

  config_parser = sub_parsers.add_parser('config', help='An example config')
  config_parser.set_defaults(cmd='config')

  help_parser = sub_parsers.add_parser('help')
  help_parser.set_defaults(cmd='help')

  args = parser.parse_args()

  if args.cmd == 'list':
    list_tasks()
  elif args.cmd == 'add':
    add_task(args.titles)
  elif args.cmd == 'complete':
    complete_tasks(args.index_range)
  elif args.cmd == 'float':
    float_task(int(args.index))
  elif args.cmd == 'sink':
    sink_task(int(args.index))
  elif args.cmd == 'remove':
    remove_tasks(args.index_range)
  elif args.cmd == 'config':
    print "\n  An example configuration file, which you should save as ~/.workbox:\n\n[Server Name]\nbase_url = https://foo.com/wiki\nusername = xxx\npassword = yyy\n"
  elif args.cmd == 'help':
    parser.print_help()

if __name__ == '__main__':
  main()
