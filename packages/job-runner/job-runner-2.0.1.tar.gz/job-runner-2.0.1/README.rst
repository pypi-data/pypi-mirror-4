Job-Runner
==========

.. image:: https://api.travis-ci.org/spilgames/job-runner.png?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/spilgames/job-runner

**Job-Runner** is a crontab like tool, with a nice web-frontend for
administration and (live) monitoring the current status. It is possible to
schedule recurring jobs, chaining jobs and the option to run or kill jobs
ad-hoc (from the dashboard). As well it provides permission management
(eg: so that some people are able to only see jobs on the dashboard, where
other people are also able to start them ad-hoc or kill them).

The whole project consists of three separate components (and repositories):

* **Job-Runner**: provides the REST interface, admin interface and (live)
  dashboard. As well this component provides a long-running process
  (``manage.py broadcast_queue``) to broadcast messages (over ZeroMQ) to the
  workers. See: https://github.com/spilgames/job-runner

* **Job-Runner Worker**: the process that is responsible for executing the job.
  It subscribes to (ZeroMQ) messages coming from ``broadcast_queue``, send data
  back over the REST interface and publishes events to the
  *Job-Runner WebSocket Server*.
  You can run as many workers as you like, as long as every worker has it's own
  API key (eg: when you want to run jobs on multiple servers or under different
  usernames on the same server). API keys can be created in the *Job-Runner*
  admin interface.
  See: https://github.com/spilgames/job-runner-worker

* **Job-Runner WebSocket Server**: will subscribe to *Job-Runner Worker* events
  and re-broadcast them to WebSocket connections coming from the *Job-Runner*
  dashboard. This makes it possible to add realtime monitoring to the
  dashboard.
  See: https://github.com/spilgames/job-runner-ws-server


Links
-----

* `documentation <https://job-runner.readthedocs.org/>`_
* `job-runner source <https://github.com/spilgames/job-runner>`_
* `job-runner-worker source <https://github.com/spilgames/job-runner-worker>`_
* `job-runner-ws-server source <https://github.com/spilgames/job-runner-ws-server>`_


Changes
-------

v2.0.1
~~~~~~

* Optimize the way how the ``ModelAuthorization`` class is testing if the user
  or worker has access to the object.


v2.0.0
~~~~~~

* Restructure the relations between models. Workers are now project independent
  and are grouped by pools. Permissions are now managed on project level
  (instead on project and job-template level) By assigning a job to a pool
  containing multiple workers, the job will be loadbalanced
  (by selecting a random worker).

  After upgrading, make sure to run ``manage.py migrate`` to migrate your
  data to the new structure.

  .. warning:: Before running ``manage.py migrate``, make a backup of your
               data! The new structure is not backwards compatible and
               thus can not be migrated backwards.


v1.4.3
~~~~~~

* Fix duplicated enqueues when the worker is down or the enqueue is disabled
  for the job. This happened for example when a parent-job tried to schedule
  a child job which was disabled.


v1.4.2
~~~~~~

* Fix the issue where runs from other projects than the selected one, were
  rendered on the dashboard.


v1.4.1
~~~~~~

* Add caching of objects to improve the performance (frontend).


v1.4.0
~~~~~~

* Complete refactor of front-end code. The front-end is now based on AngularJS.
* Misc admin interface improvements (sorting, labels, etc...).
* Add if the run was manual and / or killed to the error e-mail template.
* Add compressor for JavaScript code.


v1.3.3
~~~~~~

* Broadcast ping requests to the worker (default: every 5 minutes) and show
  last ping response in admin. This will make it more easy to discover problems
  with workers.


v1.3.2
~~~~~~

* Spil specific settings removed.


v1.3.1
~~~~~~

* Fix run status modal JavaScript code (was not working when there is no log
  yet).
* Fix related name of ``run_log``, to make sure it shows up correctly in the
  template when there is an error.


v1.3.0
~~~~~~

* Move logs to separate model and RESTful resource. Make sure that you update
  the worker to >= v1.1.0.


v1.2.10
~~~~~~~

* Show full path (project - template - worker ...) in object title.
* Improve ordering of objects in the admin.
* Added getting started section to the docs.
* Misc documentation improvements.


v1.2.9
~~~~~~

* Fix kill button so that it is only visible when the user has permission to
  kill a job-run (would else result in a HTTP error).


v1.2.8
~~~~~~

* Add option in dashboard to kill job-runs.
* Fix time-zone in failed-run e-mail template (will now use the time-zone
  configured in the Django config).


v1.2.7
~~~~~~

* Disable the job when it failed more than x times (optional setting).


v1.2.6
~~~~~~

* Make it possible to disable the enqueue of a project, worker or job-template.


v1.2.5
~~~~~~

* Display parent - child relationships in job details.
* Fix an other issue with the run broadcaster to make sure it doesn't broadcast
  multiple runs for the same job.
* Fix styling glitches by adding a ``boot.css`` which is used as long the
  ``.less`` files aren't compiled yet.


v1.2.4
~~~~~~

* Fix run broadcaster so that it doesn't send runs to the workers when there
  is still an other run for the same job active (in queue or started).
* Fix autoselect environment settings.
* Update hostnames in configuration.


v1.2.3
~~~~~~

* Add filters to limit the number of displayed jobs.
* Add status icon to display if there is a connection with the WebSocket server
* Add option for monthly re-scheduling **Note:** monthly re-scheduling works
  by incrementing the ``dts`` with the number of days that are in the ``dts``.
  When incrementing by multiple months, it will check the days for each month.


v1.2.2
~~~~~~

* Add description fields to projects, workers, job-templates and jobs
* Add ``TransactionMiddleware``
* Fix rescheduling when two runs are active of the same job


v1.2.1
~~~~~~

* Add MySQL to requirements.txt (since the python setup.py install is
  creating a zipped .egg which doesn't work when the user does not have
  a homedir (or when the homedir is not executable).


v1.2.0
~~~~~~

* Show job details in a column instead of a modal
* Show last 100 runs of a job incl. duration graph
* Fix ``AUTHENTICATION_BACKENDS`` setting for staging and production
  (without ``ModelBackend`` included, permissions are not working!)
* A job-title must now be unique per job-template
* Show re-schedule interval in job details


v1.1.1
~~~~~~

* Fix dependencies in ``setup.py`` (was not using the development version
  from GitHub).


v1.1.0
~~~~~~

* Run and job details are made deeplinkable
* Runs and jobs that are suspended are greyed-out


v1.0.0
~~~~~~

* Fix size (height) of run / job headers
* Fix order of run objects
* Fix escaping of HTML characters in job script and log output
* Enable timezone, all data is now presented (and expected to be) in the
  *Europe/Amsterdam* timezone
* Order scheduled runs ascending (first to run on top)
* Add option to schedule children or not, when manually scheduling runs

v0.7.4
~~~~~~

* Internal related changes.


v0.7.3
~~~~~~

* Add ``job_runner.settings.env.production_longrun`` settings module for long
  running processes to avoid "cached" results.


v0.7.2
~~~~~~

* Fix issue where filtering the groups would result in duplicated results.
* Remove WebKit browser notifications, since it was breaking the front-end in
  Firefox.


v0.7.1
~~~~~~

* Check that runs received from the WebSocket server are within the current
  active project.
* Add WebKit browser notifications.


v0.7.0
~~~~~~

* **Major refactor:** It is now possible to use AD assigned groups when
  creating projects. Since basically all models are changed / renamed, it was
  not possible to migrate old data to the new structure. Therefore you should
  re-create the database!
* Add ``broadcast_queue`` management command to publish enqueueable runs to
  the workers.


v0.6.2
~~~~~~

* Add missing static-file and logging settings.


v0.6.1
~~~~~~

* Add MySQL package as a requirement + update requirements in docs.
* Make it possible to override production settings.


v0.6.0
~~~~~~

* Create standalone application.
* Add overview of jobs + scheduling.
