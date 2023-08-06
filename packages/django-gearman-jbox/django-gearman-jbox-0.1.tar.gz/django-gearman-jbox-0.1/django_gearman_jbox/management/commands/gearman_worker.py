# -*- coding: utf-8 -*-

import os
import signal
import sys

from optparse import make_option

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django_gearman_jbox import GearmanWorker

class Command(NoArgsCommand):

  help = "Start a Gearman worker serving all registered Gearman jobs"
  __doc__ = help

  ALL_QUEUES = '*'

  option_list = NoArgsCommand.option_list + (
    make_option('-a', '--app-name', action='store', dest='app_name', default=None, help='Django App where workers are stored'),
    make_option('-n', '--worker-name', action='store', dest='worker_name', default=None, help='Name of the worker to start'),
    make_option('-q', '--queue-name', action='store', dest='queue_name', default=ALL_QUEUES, help='Name of the worker to start'),
  )


  @staticmethod
  def get_gearman_worker(app_name, worker_name):
    try:
      worker = __import__("%s.gearman_workers.%s" % (app_name, worker_name))
    except ImportError:
      return None
    else:
      return worker


  def handle_noargs(self, **options):
    app_name    = options["app_name"]
    worker_name = options["worker_name"]
    queue_name  = options["queue_name"]

    if not app_name:
      self.stderr.write("Need Django App name ! \n")
      return

    if not worker_name:
      self.stderr.write("Need Gearman Worker name ! \n")
      return

    # find gearman worker
    worker = Command.get_gearman_worker(app_name, worker_name)
    if not worker:
      self.stderr.write("Gearman Worker '%s' not found ! \n" % worker_name)
      return

    try:
      worker.tasks_list
    except AttributeError:
      self.stderr.write("No Gearman Tasks found at all ! \nCheck your decorators ! \n")
      return

    self.stdout.write("\n--------------------------------\n")
    self.stdout.write("Available Queues and Tasks : \n")
    for queue, tasks in worker.tasks_list.items():
      self.stdout.write("\nQueue: %s\n" % queue)
      self.stdout.write("Tasks:\n")
      for task in tasks:
        self.stdout.write(" * %s\n" % task.__name__)
    self.stdout.write("--------------------------------\n\n")

    tasks = []
    # find all queues therefore all tasks
    if queue_name == Command.ALL_QUEUES:
      for _tasks in worker.tasks_list.itervalues():
        tasks += _tasks
    else:
      # find tasks for specific queue
      tasks += worker.tasks_list.get(queue_name, [])

    if not tasks:
      self.stderr.write("Gearman Queue '%s' not found ! \n\n" % queue_name)
      return

    self.work(worker_name, queue_name, tasks)


  def work(self, worker_name, queue_name, tasks):
    worker = GearmanWorker()
    for task in tasks:
      worker.register_task(task.__name__, task)

    # catch SIGINT and SIGTERM
    setSignalHandler(worker_name)

    self.stdout.write("\n----------------------------------\n")
    self.stdout.write("Queue '%s' launched with tasks : \n" % queue_name)
    for task in tasks:
      self.stdout.write("* %s\n" % task.__name__)
    self.stdout.write("----------------------------------\n")

    # start for real
    worker.work()


class setSignalHandler:
  """
  setSignalHandler
  """
  def __init__(self, worker_name):
    self.worker_name = worker_name
    signal.signal(signal.SIGTERM, self.myHandler)
    signal.signal(signal.SIGINT, self.myHandler)

  def myHandler(self, s, f):
    print "%s get interrupted, exiting..." % self.worker_name
    sys.exit(0)
