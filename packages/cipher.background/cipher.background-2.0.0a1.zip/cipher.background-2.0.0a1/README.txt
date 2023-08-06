cipher.background
=================

A library for creating background threads that can talk to the ZODB and use
local site components.

We're probably reinventing Celery.


Example
-------

Let's assume we have a DMS with a simple publication workflow. We
have two states "DRAFT" and "PUBLISH". The Problem in this example
is: that the transition form "DRAFT" to "PUBLISH" takes some minutes,
and we don't want the user to be waiting.

First we have create a WorkflowTransition-BackgroundThread:

.. code-block:: python

    class MyWorkflowTransition(BackgroundWorkerThread):
        execute = True
        description = "background worker thread (%(class_name)s) for %(site_name)s User %(user_name)s"

        def __init__(self, site_db, site_oid, site_name, user_name, daemon=True, object_oid=None):
            self.object_oid = object_oid
            super(MyWorker, self).__init__(site_db, site_oid, site_name, user_name, daemon=True)

        def scheduleNextWork(self):
            return self.execute

        def getObjectFromOID(self):
            conn = getSite()._p_jar
            return conn.get(self.object_oid)

        def doWork(self):
            sleep(15) # This is our long TASK
            self.execute = False
            document = self.getObjectFromOID()
            document.wf_status = "PUBLISHED"


We have a simple Document with an initial Workflow-State draft.

.. code-block:: python

   class Document(Persistent):
       wf_state = "DRAFT"


Now we have to call our WorkflowTransition.

.. code-block:: python

    def setWorkflow(site, document_oid, user_name):
        worker = MyWorkflowTransition(
            site_db = site._p_jar.db(), 
            site_oid = site._p_oid,
            site_name = site.__name__,
            user_name = user_name,
            object_oid = document_oid,
            )
        worker.start()

When calling worker.start() the thread goes into "Background" and the user
don't have to wait until the Transition is finished.

