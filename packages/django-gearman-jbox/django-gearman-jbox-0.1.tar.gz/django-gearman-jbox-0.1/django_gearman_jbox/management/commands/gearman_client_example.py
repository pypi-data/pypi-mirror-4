# -*- coding: utf-8 -*-

from django.core.management.base import NoArgsCommand

from django_gearman_jbox import GearmanClient


class Command(NoArgsCommand):

  help = "Execute an example command with the django_gearman interface"
  __doc__ = help

  def handle_noargs(self, **options):

    client = GearmanClient()

    sentence = "The quick brown fox jumps over the lazy dog."

    print "\nReversing example sentence: '%s' \n" % sentence

    print "Asynchronous Gearman Call"
    print "------------------------"
    res1 = client.submit_job("worker_foo", background=True, kwargs={"sentence": sentence})
    print "Result: '%s' \n" % res1.result

    print ""

    print "Synchronous Gearman Call"
    print "------------------------"
    res2 = client.submit_job("foo", kwargs={"sentence": sentence})
    print "Result: '%s' \n" % res2.result

    print ""

    print "Asynchronous Gearman Call"
    print "------------------------"
    sentence1 = "The quick brown fox"
    sentence2 = "jumps over the lazy dog."
    res3 = client.submit_job("foofoo", background=True, kwargs={"sentence1": sentence1, "sentence2":sentence2})
    print "Result: '%s' \n" % res3.result
