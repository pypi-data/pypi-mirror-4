.. retask documentation master file, created by
   sphinx-quickstart on Tue Jul  3 14:56:38 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Retask: simple Task Queue
=============================
retask is a python module to create and manage distributed task queue/job queue.

It uses `Redis <http://redis.io>`_ to create task queues. User can enqueue
and dequeue tasks in the queues they manage. Each task can contain any JSON
serializable python objects. We use `JSON` internally to store the tasks
in the queues.

Workers can execute tasks and return the result asynchronously and if required
synchronously (wait until worker returns the result to the job).

Dependencies
------------
- python-redis
- mock
- A running Redis server



User Guide
----------


.. toctree::
   :maxdepth: 2

   user/intro
   user/redis
   user/install
   user/quickstart
   user/tutorials



API Documentation
-----------------

.. toctree::
   :maxdepth: 2

   api

Indices and tables
------------------

* :ref:`genindex`

