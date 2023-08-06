# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

import django_gearman_jbox.settings

from django_gearman_jbox import GearmanServerInfo


class Command(BaseCommand):
  """
  Pprint overview of Gearman server status and workers
  """

  args = '[task_filter]'
  help = 'Print overview of Gearman server status and workers.'

  def handle(self, *args, **options):
    result = ''

    task_filter = ''
    if len(args) > 0:
      task_filter = args[0]

    for server in jbox_gearman.settings.GEARMAN_CLIENT_SERVERS:
      try:
        server_info = GearmanServerInfo(server)
        result += server_info.get_server_info(task_filter)
      except:
        result += '\n##############################\n\n'
        result += "Server '%s' is Down ! \n" % server
        result += '\n##############################\n\n'

    self.stdout.write(result)
