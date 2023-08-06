# -*- coding: utf-8 -*-

def gearman_task(queue='default', name=None):
  """
  Decorator turning a function inside some_app/gearman_workers/my_worker.py into a
  Gearman Worker with Tasks and Queues
  """

  class gearman_task_cls(object):

    def __init__(self, f):
      self.f = f

      # set the custom task name
      self.__name__ = name

      # if it's null, set the import name as the task name
      # this also saves one line (no else clause) :)
      if not name:
        self.__name__ = '.'.join(
          (f.__module__.replace('.gearman_workers', ''), f.__name__)
        )

      self.queue = queue

      # Store function in per-app task list
      worker = __import__(f.__module__)
      try:
        worker.tasks_list[queue].append(self)
      except KeyError:
        worker.tasks_list[queue] = [self]
      except AttributeError:
        worker.tasks_list = {self.queue: [self]}


    def __call__(self, worker, job, *args, **kwargs):
      # Call function with argument passed by the client only.
      job_args = job.data
      return self.f(*job_args["args"], **job_args["kwargs"])


  return gearman_task_cls
