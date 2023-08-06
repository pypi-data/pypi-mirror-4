# -*- coding: utf-8 -*-

import gearman
import pickle

import django_gearman_jbox.settings


class PickleDataEncoder(gearman.DataEncoder):
  @classmethod
  def encode(cls, encodable_object):
    return pickle.dumps(encodable_object)

  @classmethod
  def decode(cls, decodable_string):
    return pickle.loads(decodable_string)


class DjangoGearmanClient(gearman.GearmanClient):
  """
  Gearman client, automatically connecting to server
  """

  data_encoder = PickleDataEncoder

  def __call__(self, func, arg, uniq=None, **kwargs):
    raise NotImplementedError('Use do_task() or dispatch_background_task() instead')


  def __init__(self, **kwargs):
    """
    instantiate Gearman client with servers from settings file
    """
    return super(DjangoGearmanClient, self).__init__(django_gearman_jbox.settings.GEARMAN_CLIENT_SERVERS, **kwargs)


  def parse_data(self, arg, args=None, kwargs=None, *arguments, **karguments):
    data = {
      "args": [],
      "kwargs": {}
    }

    # The order is significant:
    # - First, use pythonic *args and/or **kwargs.
    # - If someone provided explicit declaration of args/kwargs, use those
    #   instead.
    if arg:
      data["args"] = [arg]
    elif arguments:
      data["args"] = arguments
    elif args:
      data["args"] = args

    data["kwargs"].update(karguments)
    data["kwargs"].update(kwargs)

    return data


  def submit_job(
    self, task, orig_data = None, unique=None, priority=None,
    background=False, wait_until_complete=True, max_retries=0,
    poll_timeout=None, args=None, kwargs=None, *arguments, **karguments):
    """
    Handle *args and **kwargs before passing it on to GearmanClient's
    submit_job function
    """
    data = self.parse_data(orig_data, args, kwargs, *arguments, **karguments)

    return super(DjangoGearmanClient, self).submit_job(
        task, data, unique, priority, background, wait_until_complete,
        max_retries, poll_timeout)


  def dispatch_background_task(
    self, func, arg = None, uniq=None, high_priority=False, args=None,
    kwargs=None, *arguments, **karguments):
    """
    Submit a background task and return its handle
    """

    priority = None
    if high_priority:
      priority = gearman.PRIORITY_HIGH

    request = self.submit_job(func, arg, unique=uniq,
        wait_until_complete=False, priority=priority, args=args,
        kwargs=kwargs, *arguments, **karguments)

    return request


class DjangoGearmanWorker(gearman.GearmanWorker):
  """
  Gearman worker, automatically connecting to server and discovering
  available jobs.
  """
  data_encoder = PickleDataEncoder

  def __init__(self, **kwargs):
    """
    Instantiate Gearman worker with servers from settings file
    """
    return super(DjangoGearmanWorker, self).__init__(django_gearman_jbox.settings.GEARMAN_WORKER_SERVERS, **kwargs)


  def on_job_exception(self, current_job, exc_info):
    print "%s" % exc_info[1]
    return super(DjangoGearmanWorker, self).on_job_exception(current_job, exc_info)


class DjangoGearmanServerInfo():
  """
  Administration informations about Gearman server.
  """

  def __init__(self, host):
    self.host = host
    self.server_version = None
    self.tasks = None
    self.workers = None
    self.ping_time = None
    self.ping_time_str = None

  def get_server_info(self, task_filter=None):
    """
    Read Gearman server info - status, workers and and version
    """
    result = ''

    # Read server status info.
    client = gearman.GearmanAdminClient([self.host])

    self.server_version = client.get_version()
    self.tasks = client.get_status()
    self.workers = client.get_workers()
    self.ping_time = client.ping_server()
    self.ping_time_str = '{0:0.016f}'.format(self.ping_time)

    # if task_filter is set, filter list of tasks and workers by regex pattern task_filter
    if task_filter:
      # filter tasks
      self.tasks = [item for item in self.tasks if task_filter in item['task']]

      # filter workers by registered task name
      self.workers = [item for item in self.workers if item['tasks'] and task_filter in [t for t in item['tasks']]]

    # sort tasks by task name
    self.tasks = sorted(self.tasks, key=lambda item: item['task'])

    # sort registered workers by task name
    self.workers = sorted(self.workers, key=lambda item: item['tasks'])

    # Use prettytable if available, otherwise raw output.
    try:
      from prettytable import PrettyTable
    except ImportError:
      PrettyTable = None

    if PrettyTable is not None:
      # Use PrettyTable for output.
      # version
      table = PrettyTable(['Gearman Server Host', 'Gearman Server Version', 'Ping Response Time'])
      table.add_row([self.host, self.server_version, self.ping_time_str])
      result += '{0:s}.\n\n'.format(table)

      # tasks
      table = PrettyTable(['Task Name', 'Total Workers', 'Running Jobs', 'Queued Jobs'])
      for r in self.tasks:
        table.add_row([r['task'], r['workers'], r['running'], r['queued']])

      result += '{0:s}.\n\n'.format(table)

      # workers
      table = PrettyTable(['Worker IP', 'Registered Tasks', 'Client ID', 'File Descriptor'])
      for r in self.workers:
        if r['tasks']: # ignore workers with no registered task
          table.add_row([r['ip'], ','.join(r['tasks']), r['client_id'], r['file_descriptor']])

      result += '{0:s}.\n\n'.format(table)

    else:
      # raw output without PrettyTable
      result += 'Gearman Server Host:{0:s}\n'.format(self.host)
      result += 'Gearman Server Version:{0:s}.\n'.format(self.server_version)
      result += 'Gearman Server Ping Response Time:{0:s}.\n'.format(self.ping_time_str)
      result += 'Tasks:\n{0:s}\n'.format(self.tasks)
      result += 'Workers:\n{0:s}\n'.format(self.workers)

    return result
