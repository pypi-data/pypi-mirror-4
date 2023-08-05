======
README
======

This package offers a remote processor. This remote processor is implemented as 
a simple object using the mongodb as storage. The processor can execute pre
defined jobs in another thread. It is also possible to run jobs at specific
time using the different scheduler items.

The RemoteProcessor uses two different processor. One processes jobs and the
other pickes items from the scheduler and is adding jobs. This separation
is usefull if you implement a distributed concept. This means one or more
application can schedule job items based on the given scheduler items. And
another application is processing jobs and doesn't know about how to scheduling
next items.

Since we use this remote scheduler for low CPU intensive jobs, we offer multi
processing. This is done by running more then one worker in the main worker
thread. If you use subprocess for your job processing, you will get a real
multiprocessing processor which isn't limited to the current python process.

You can configure the amount of threads which a job worker can start in the 
remote processor. See jobWorkerArguments/maxThreads. By default this number
uses the amount of CPU installed on your machine.

The implementation uses a mongodb as a storage for it's component. This means
jobs, job factories and scheduler items get stored in the mongodb using the
ORM concept given from m01.mongo.

See p01.remote for a ZODB based remote processor implementation but take care
the p01.remote implementation doesn't provide the worker and scheduler
processor separation. At least not yet.


Usage
-----

  >>> import transaction
  >>> from pprint import pprint
  >>> from m01.mongo import UTC
  >>> import zope.component
  >>> import m01.remote.job
  >>> from m01.remote import testing

First register our error message adapter:

  >>> testing.setUpJobErrorMessageAdapter()

Let's now start by create two a remote processor. We can use our remote queue
site implementation:

  >>> from zope.security.proxy import removeSecurityProxy
  >>> from m01.remote import interfaces

Our test remote processor should be available as application root:

  >>> rp = root
  >>> rp
  <TestProcessor None>

Let's discover the available jobs:

  >>> dict(root._jobs)
  {}

The job container is initially empty, because we have not added any job
factory. Let's now define a job factory that simply echos an input string:

  >>> echoJob = testing.EchoJob({})

Now we can set the job input:

  >>> echoJob.input = {'foo': u'blah'}

The only API requirement on the job is to be callable. Now we make sure that
the job works. Note we call our job with the remote processor instance which
is our initialized application root:

  >>> echoJob(root)
  {'foo': u'blah'}

Let's add the job to the available job list:

  >>> rp.addJobFactory(u'echo', echoJob)

The echo job is now available in the remote processor:

  >>> dict(rp._jobFactories)
  {u'echo': <EchoJob u'echo'>}

Since the remote processor cannot instantaneously complete a job, incoming jobs
are managed by a queue. First we request the echo job to be executed:

  >>> jobid1 = rp.addJob(u'echo', {'foo': 'bar'})
  >>> jobid1
  u'...'

  >>> sorted([job.status for job in rp._jobs.values()])
  [u'queued']

The ``addJob()`` function schedules the job called "echo" to be executed
with the specified arguments. The method returns a job id with which we can
inquire about the job. The ``addJob()`` function marks a job as queued.

  >>> rp.getJobStatus(jobid1)
  u'queued'

Since the job has not been processed, the status is set to "queued". Further,
there is no result available yet:

  >>> rp.getJobResult(jobid1) is None
  True

As long as the job is not being processed, it can be cancelled:

  >>> rp.cancelJob(jobid1)
  >>> rp.getJobStatus(jobid1)
  u'cancelled'

  >>> sorted([job.status for job in rp._jobs.values()])
  [u'cancelled']

The worker processor isn't being started by default:

  >>> rp.isProcessing
  False

To get a clean logging environment let's clear the logging stack::

  >>> log_info.clear()

Now we can start the remote processor by calling ``startProcessor``:

  >>> rp.startProcessor()

and voila - the remote processor is processing:

  >>> rp.isProcessing
  True

Checking out the logging will prove the started remote processor:

  >>> print log_info
  m01.remote INFO
    Processor 'root-worker' started

Let's stop the processor again:

  >>> rp.stopProcessor()
  >>> rp.isProcessing
  False

Now let's get a result from a processed job but first commit the new added job:

  >>> jobid2 = rp.addJob(u'echo', {'foo': u'bar'})
  >>> transaction.commit()

  >>> sorted([job.status for job in rp._jobs.values()])
  [u'cancelled', u'queued']

Now create a worker and process the new jobs by calling our simple worker:

  >>> class FakeWorker(object):
  ... 
  ...     def __init__(self, rp):
  ...         self.rp = rp
  ... 
  ...     def __call__(self):
  ...         try:
  ...             result = self.rp.processNextJob()
  ...             transaction.commit()
  ...         except Exception, error:
  ...             transaction.commit()

  >>> worker = FakeWorker(rp)
  >>> worker()

  >>> sorted([job.status for job in rp._jobs.values()])
  [u'cancelled', u'completed']

First check if the job get processed:

  >>> rp.getJobStatus(jobid2)
  u'completed'

  >>> rp.getJobResult(jobid2)
  {u'foo': u'bar'}

Now, let's define a new job that causes an error:

  >>> errorJob = testing.ErrorJob()
  >>> rp.addJobFactory(u'error', errorJob)

Now add and execute it:

  >>> jobid3 = rp.addJob(u'error')
  >>> transaction.commit()
  >>> worker()

  >>> sorted([job.status for job in rp._jobs.values()])
  [u'cancelled', u'completed', u'error']

Let's now see what happened:

  >>> rp.getJobStatus(jobid3)
  u'error'
  >>> rp.getJobErrors(jobid3)
  [u'[...-...-...T...:...:...+...:...] An error occurred.']

Try at also with a not so nice error:

  >>> fatalJob = testing.FatalErrorJob()
  >>> rp.addJobFactory(u'fatal', fatalJob)

Now add and execute it:

  >>> jobid4 = rp.addJob(u'fatal')
  >>> transaction.commit()
  >>> worker()

  >>> sorted([job.status for job in rp._jobs.values()])
  [u'cancelled', u'completed', u'error', u'queued']

  >>> job4 = rp._jobs[jobid4]
  >>> job4.retryCounter
  1
  >>> job4.status == u'queued'
  True

  >>> job4.errors
  [u'[...-...-...T...:...:...+...:...] An error occurred.']

And process the job again but first set our retryTime to an outdated value which
will simulate that time passes since our last call:

  >>> import datetime
  >>> job4.retryTime = datetime.datetime(2000, 1, 1, tzinfo=UTC)
  >>> transaction.commit()
  >>> worker()

  >>> sorted([job.status for job in rp._jobs.values()])
  [u'cancelled', u'completed', u'error', u'queued']

  >>> job4 = rp._jobs[jobid4]
  >>> job4.retryCounter
  2

  >>> job4.errors
  [u'[...-...-...T...:...:...+...:...] An error occurred.',
   u'[...-...-...T...:...:...+...:...] An error occurred.']

And process the job again the 3rd time. Now it does not re-raise the exception
but the error message get appended to the error list.

  >>> job4.retryTime = datetime.datetime(2000, 1, 1, tzinfo=UTC)
  >>> transaction.commit()
  >>> worker()

  >>> sorted([job.status for job in rp._jobs.values()])
  [u'cancelled', u'completed', u'error', u'error']

Let's now see what happened:

  >>> job4 = rp._jobs[jobid4]
  >>> job4.retryCounter
  3

  >>> job4.status
  u'error'

  >>> rp.getJobStatus(jobid4)
  u'error'

  >>> job4.errors
  [u'[...-...-...T...:...:...+...:...] An error occurred.',
   u'[...-...-...T...:...:...+...:...] An error occurred.',
   u'[...-...-...T...:...:...+...:...] An error occurred.']

  >>> rp.getJobErrors(jobid4)
  [u'[...-...-...T...:...:...+...:...] An error occurred.',
   u'[...-...-...T...:...:...+...:...] An error occurred.',
   u'[...-...-...T...:...:...+...:...] An error occurred.']

For management purposes, the remote processor also allows you to inspect all
jobs:

  >>> pprint(dict(rp._jobs))
  {u'...': <EchoJob u'...' ...>,
   u'...': <EchoJob u'...' ...>,
   u'...': <ErrorJob u'...' ...>,
   u'...': <FatalErrorJob u'...' ...>}


To get rid of jobs not needed anymore we can use the reomveJobs method.

  >>> jobid8 = rp.addJob(u'echo', {'blah': 'blah'})
  >>> transaction.commit()

  >>> sorted([job.status for job in rp._jobs.values()])
  [u'cancelled', u'completed', u'error', u'error', u'queued']

  >>> rp.removeJobs()
  {u'cancelled': 1, u'completed': 1, u'error': 2}

  >>> sorted([job.status for job in rp._jobs.values()])
  [u'queued']

Now process the last pending job and make sure we do not get more jobs:

  >>> rp.pullNextJob()
  <EchoJob u'...' ...>


Threading behavior
------------------

Each remote processor runs in a separate thread, allowing them to operate
independently. Jobs should be designed to avoid conflict errors.

Let's start the remote processor we have defined at this point, and see what
threads are running as a result::

  >>> rp.startProcessor()

  >>> import pprint
  >>> import threading

  >>> def show_threads():
  ...     threads = [t for t in threading.enumerate()
  ...                if t.getName().startswith('root')]
  ...     threads.sort(key=lambda t: t.getName())
  ...     pprint.pprint(threads)

  >>> show_threads()
  [<Thread(root-worker, started daemon ...)>]

Let's stop the remote processor, and give the background threads a chance to get
the message::

  >>> rp.stopProcessor()

  >>> import time
  >>> time.sleep(2)

The threads have exited now::

  >>> print [t for t in threading.enumerate()
  ...        if t.getName().startswith('root')]
  []
