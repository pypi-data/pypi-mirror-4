django-gearman-jbox
===================

*django-gearman-jbox* is a convenience wrapper for the [Gearman][Gearman]
[Python Bindings][python-gearman].

With django-gearman-jbox, you can code workers as well as clients in a Django project
with minimal overhead in your application. Server connections etc. all take
place in django-gearman-jbox and don't unnecessarily clog your application code.

This library is based in large part on Fred Wenzel's [django-gearman] and Jozef Ševčík's [django-gearman-commands].
- [django-gearman][django-gearman] for the 'decorator way' to create workers (very cool)
- [django-gearman-commands][django-gearman-commands] for the 'gearman_server_info' command (very nice)

But there are some modifications :

Workers are now launched individually, so you have to pass 2 mandatory parameters to start the worker :
 - the Django App name where workers reside with the `-a` parameter
 - the worker's name with `-n`

The `-q` parameter is still here and has the same function than in [django-gearman].

- I removed the ability of lauching many wokers at once (`-w` parameter in [django-gearman]).
I prefer having one process for each worker and Supervisord managing process. (screen is not an option)
- I also added a signal handler to catch SIGTERM signals send by Supervisord and SIGINT when you worker is attached to the console.
This gives you the possibility of executing code just before the worker terminates.
(See `django_gearman_jbox\management\commands\gearman_worker.py`, line 116)

[Gearman]: http://gearman.org
[python-gearman]: http://github.com/samuel/python-gearman
[django-gearman]: https://github.com/fwenzel/django-gearman
[django-gearman-commands]: https://github.com/CodeScaleInc/django-gearman-commands


Installation
------------
It's the same for both the client and worker instances of your django project :

    $ pip install django-gearman-jbox

Add ``django_gearman_jbox`` to the `INSTALLED_APPS` section of `settings.py`.

Specify the following setting in your local settings.py file:

    # One or more gearman servers
    GEARMAN_CLIENT_SERVERS = ['127.0.0.1']
    GEARMAN_WORKER_SERVERS = ['127.0.0.1']

Workers
-------
### Registering workers
Create a directory `gearman_workers` in any of your django apps, and define as many
workers as you like, one worker per file. Create an empty `__init__.py` so the directory will be
loaded as a package.

Example :

    my_django_app
      |_ models.py
      |_ gearman_workers
          |_ __init__.py
          |_ worker_foo.py
          |_ worker_bar.py


### Registering tasks
In the worker file, you can define as many tasks as functions as you like.
The function must accept a single argument as passed by the caller and must
return the result of the operation, if applicable. (Note : It must accept an argument, even if you don't use it).

Mark each of these functions as gearman tasks by decorating them with :

    import django_gearman_jbox.decorators.gearman_task

    @gearman_task()
    def my_task_function(foo):
      pass

### Task naming
The tasks are given a default name of their import path, with the phrase
`gearman_task` stripped out of them, for readability reasons. You can override
the task name by specifying `name` parameter of the decorator. Here's how :

    import django_gearman_jbox.decorators.gearman_task

    @gearman_task(name='my-task-name')
    def my_task_function(foo):
      pass

### Task parameters
The gearman docs specify that the task function can accept only one parameter
(usually refered to as the ``data`` parameter). Additionally, that parameter
may only be a string. Sometimes that may not be enough. What if you would like
to pass an array or a dict? You would need to serialize and deserialize them.
Fortunately, django-gearman-jbox can take care of this, so that you can spend
all of your time on coding the actual task.

    @gearman_task(name='my-task-name')
    def my_task_function(foo):
      pass

    client.submit_job('my-task-name', {'foo': 'becomes', 'this': 'dict'})
    client.submit_job('my-task-name', Decimal(1.0))

### Tasks with more than one parameter

You can pass as many arguments as you want, of whatever (serializable) type
you like. Here's an example job definition :

    @gearman_task(name='my-task-name')
    def my_task_function(one, two, three):
      pass

You can execute this function in two different ways :

    client.submit_job('my-task-name', one=1, two=2, three=3)
    client.submit_job('my-task-name', args=[1, 2, 3])

Unfortunately, executing it like this:

    client.submit_job('my-task-name', 1, 2, 3)

would produce the error, because ``submit_job`` from Gearman's Python bindings
contains __a lot__ of arguments and it's much easier to specify them via
keyword names or a special ``args`` keyword than to type something like seven
``None``s instead :

    client.submit_job('my-task-name', None, None, None, None, None, None, None, 1, 2, 3)

The only limitation that you have are gearman reserved keyword parameters. As of
Gearman 2.0.2 these are :

    * data
    * unique
    * priority
    * background
    * wait_until_complete
    * max_retries
    * poll_timeout

So, if you want your task definition to have, for example, ``unique`` or
``background`` keyword parameters, you need to execute the task in a special,
more verbose way. Here's an example of such a task and its execution :

    @gearman_task(name='my-task-name')
    def my_task_function(background, unique):
      pass

    client.submit_job('my-task-name', kwargs={"background": True, "unique": False})
    client.submit_job('my-task-name', args=[True, False])

Finally:

    client.submit_job('my-task-name', background=True, unique=True, kwargs={"background": False, "unique": False})

Don't panic, your task is safe! That's because you're using ``kwargs``
directly. Therefore, Gearman's bindings would receive ``True`` for
``submit_job`` function, while your task would receive ``False``.

Always remember to double-check your parameter names with the reserved words
list.

### Starting a worker
To start a worker, run `python manage.py gearman_worker -a <django_app_name> -n <worker_name>`. It will start
serving all registered tasks for that worker.

Example :

    $ python manage.py gearman_worker -a django_app_name -n worker_foo
    $ python manage.py gearman_worker -a django_app_name -n worker_bar

To spawn more than one worker see Supervisord configuration below.

### Task queues
Queues are a virtual abstraction layer built on top of gearman tasks. An
easy way to describe it is the following example: Imagine you have a task
for fetching e-mails from the server, another task for sending the emails
and one more task for sending SMS via an SMS gateway. A problem you may
encounter is that the email fetching tasks may effectively "block" the worker
(there could be so many of them, it could be so time-consuming, that no other
task would be able to pass through). Of course, one solution would be to add
more workers (via the Supervisord), but that would only temporarily
solve the problem. This is where queues come in.

The first thing to do is to pass a queue name into the job description, like
this :

    @gearman_task(name="task_foo", queue="foo")
    def function_foo(some_arg):
      pass

    @gearman_task(name="task_bar", queue="bar")
    def function_bar(some_arg):
      pass

    @gearman_task(name="task_babar", queue="bar")
    def function_babar(some_arg):
      pass

You may then proceed to start the tasks that are bound to a specific
queue :

    python manage.py gearman_worker -a <django_app_name> -n <worker_name> -q bar

Be aware of the fact that if you don't specify the queue name, the worker
will load all tasks.

### Start workers with Supervisord
Supervisor - http://supervisord.org/ is babysitter for processes.
It allows you to launch, restart and monitor running processes. In our case it will be workers.
To do so, create one config file by worker and adjust the number of workers you want with the 'numprocs' parameter :

`worker_foo.conf` :

    [program:worker_foo]
    command         = /path-to-your-virtualenv/bin/python /path-to-your-project/manage.py gearman_worker -a <django_app_name> -n %(program_name)s
    process_name    = %(program_name)s_%(process_num)02d
    numprocs        = 1
    autostart       = true
    autorestart     = true
    user            = myapp
    directory       = /home/myapp/
    environment     = HOME='/home/myapp',USER='myapp',LOGNAME='myapp',

`worker_bar.conf` :

    [program:worker_bar]
    command         = /path-to-your-virtualenv/bin/python /path-to-your-project/manage.py gearman_worker -a <django_app_name> -n %(program_name)s -q bar
    process_name    = %(program_name)s_%(process_num)02d
    numprocs        = 2
    autostart       = true
    autorestart     = true
    user            = myapp
    directory       = /home/myapp/
    environment     = HOME='/home/myapp',USER='myapp',LOGNAME='myapp',

You can also create a `groups.conf` file with this content :

    [group:foo]
    programs=worker_foo, worker_foo2

    [group:bar]
    programs=worker_bar, worker_bar2


This will create process 'group' and allows you to reload all workers related to this group at once when you redeploy new code.

Once you're config files are created, do `/etc/init.d/supervisord start` to start Supervisord and `supervisorctl reload` if you modify config or

    supervisorctl reread
    supervisorctl update
    supervisorctl restart foo:*
    supervisorctl restart bar:*

### Execute code when workers die
Workers catch SIGTERM and SIGINT signals to kill themselves with a `sys.exit(0)` in a callback function.
At this point in the code you can add your own function(s) which will be executed before the `sys.exit(0)`
See `django_gearman_jbox\management\commands\gearman_worker.py`, line 116

Note that this will impact all workers as it resides in the `gearman_worker.py` script which is global for all workers.


Clients
-------
To make your workers work, you need a client app passing data to them.
Create and instance of the `django_gearman_jbox.GearmanClient` class and execute submit_job with it :

    from django_gearman_jbox import GearmanClient

    sentence = "The quick brown fox jumps over the lazy dog."

    client = GearmanClient()
    res = client.submit_job("foo", kwargs={"sentence": sentence})
    print "Result: '%s'" % res

Dispatching a background event without waiting for the result is easy as well :

    client.submit_job("foo", background=True, kwargs={"sentence": sentence})

Gearman Server Infos
-------------------

`python manage.py gearman_server_info` outputs current status of Gearman servers.
If you installed Prettytable dependency, here is how output looks like :

    $ python manage.py gearman_server_info
    +---------------------+------------------------+
    | Gearman Server Host | Gearman Server Version |
    +---------------------+------------------------+
    |    127.0.0.1:4730   |        OK 0.29         |
    +---------------------+------------------------+.

    +---------------+---------------+--------------+-------------+
    |   Task Name   | Total Workers | Running Jobs | Queued Jobs |
    +---------------+---------------+--------------+-------------+
    | data_unlock   |       1       |      0       |      0      |
    | data_import   |       1       |      1       |      0      |
    | cache_cleanup |       1       |      0       |      0      |
    +---------------+---------------+--------------+-------------+.

    +-----------+------------------+-----------+-----------------+
    | Worker IP | Registered Tasks | Client ID | File Descriptor |
    +-----------+------------------+-----------+-----------------+
    | 127.0.0.1 |   data_unlock    |     -     |        35       |
    | 127.0.0.1 |   data_import    |     -     |        36       |
    | 127.0.0.1 |  cache_cleanup   |     -     |        37       |
    +-----------+------------------+-----------+-----------------+

If you have a lot of workers, you can filter output using command argument (case-sensitive):

    $ python manage.py gearman_server_info cleanup
    +---------------------+------------------------+--------------------+
    | Gearman Server Host | Gearman Server Version | Ping Response Time |
    +---------------------+------------------------+--------------------+
    |    127.0.0.1:4730   |        OK 1.1.3        | 0.0006871223449707 |
    +---------------------+------------------------+--------------------+.

    +---------------+---------------+--------------+-------------+
    |   Task Name   | Total Workers | Running Jobs | Queued Jobs |
    +---------------+---------------+--------------+-------------+
    | cache_cleanup |       1       |      0       |      0      |
    +---------------+---------------+--------------+-------------+.

    +-----------+------------------+-----------+-----------------+
    | Worker IP | Registered Tasks | Client ID | File Descriptor |
    +-----------+------------------+-----------+-----------------+
    | 127.0.0.1 |  cache_cleanup   |     -     |        37       |
    +-----------+------------------+-----------+-----------------+

Licensing
---------
This software is licensed under the [Mozilla Tri-License][MPL]:

    ***** BEGIN LICENSE BLOCK *****
    Version: MPL 1.1/GPL 2.0/LGPL 2.1

    The contents of this file are subject to the Mozilla Public License Version
    1.1 (the "License"); you may not use this file except in compliance with
    the License. You may obtain a copy of the License at
    http://www.mozilla.org/MPL/

    Software distributed under the License is distributed on an "AS IS" basis,
    WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
    for the specific language governing rights and limitations under the
    License.

    The Original Code is django-gearman.

    The Initial Developer of the Original Code is Mozilla.
    Portions created by the Initial Developer are Copyright (C) 2010
    the Initial Developer. All Rights Reserved.

    Contributor(s):
      Frederic Wenzel <fwenzel@mozilla.com>>
      Jeff Balogh <me@jeffbalogh.org>
      Jonas <jvp@jonasundderwolf.de>
      Jozef Ševčík <sevcik@codescale.net>
      Nicolas Rodriguez <nrodriguez@jbox-web.com>

    Alternatively, the contents of this file may be used under the terms of
    either the GNU General Public License Version 2 or later (the "GPL"), or
    the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
    in which case the provisions of the GPL or the LGPL are applicable instead
    of those above. If you wish to allow use of your version of this file only
    under the terms of either the GPL or the LGPL, and not to allow others to
    use your version of this file under the terms of the MPL, indicate your
    decision by deleting the provisions above and replace them with the notice
    and other provisions required by the GPL or the LGPL. If you do not delete
    the provisions above, a recipient may use your version of this file under
    the terms of any one of the MPL, the GPL or the LGPL.

    ***** END LICENSE BLOCK *****

[MPL]: http://www.mozilla.org/MPL/
