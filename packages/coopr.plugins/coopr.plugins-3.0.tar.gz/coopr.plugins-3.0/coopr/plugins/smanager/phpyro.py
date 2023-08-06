#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2011 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


__all__ = ["PHSolverServerAction"]

try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import Pyro.core
    import pyutilib.pyro
    using_pyro=True
except ImportError:
    using_pyro=False
import time

import pyutilib.misc
import pyutilib.component.core
from pyutilib.enum import Enum

from coopr.opt.parallel.manager import *
from coopr.opt.parallel.async_solver import *
from coopr.opt.results import SolverResults


# 
# an enumerated type used to define specific actions for a PH solver server.
#

PHSolverServerAction = Enum(
   'solve' # perform a scenario solve using whatever data is available
)

#
# a specialized asynchronous solver manager for Progressive Hedging.
#

class SolverManager_PHPyro(AsynchronousSolverManager):

    pyutilib.component.core.alias('phpyro')

    def clear(self):
        """
        Clear manager state
        """
        AsynchronousSolverManager.clear(self)
        self.client = pyutilib.pyro.Client()
        self._verbose = False
        self._ah = {}

    def _perform_queue(self, ah, *args, **kwds):
        """
        Perform the queue operation.  This method returns the ActionHandle,
        and the ActionHandle status indicates whether the queue was successful.
        """

        # the PH solver server expects no non-keyword arguments. 
        if len(args) > 0:
           raise RuntimeError("ERROR: The _perform_queue method of PH pyro solver manager received position input arguments, but accepts none.")

        if "action" not in kwds:
           raise RuntimeError("ERROR: No 'action' keyword supplied to _perform_queue method of PH pyro solver manager")

        if "name" not in kwds:
           raise RuntimeError("ERROR: No 'name' keyword supplied to _perform_queue method of PH pyro solver manager")
        instance_name = kwds["name"]

        if "verbose" in kwds:
            self._verbose = kwds["verbose"]
        else:
            # we always want to pass a verbose flag to the solver server.
            kwds["verbose"] = False 

        #
        # Pickl everything into one big data object via the "Bunch" command and post the task.
        #
        data=pyutilib.misc.Bunch(**kwds)

        # NOTE: the task type (type=) should be the name of the scenario/bundle!

        task = pyutilib.pyro.Task(data=data, id=ah.id)
        self.client.add_task(task, verbose=self._verbose, override_type=instance_name)
        self._ah[task.id] = ah

        return ah

    def _perform_wait_any(self):
        """
        Perform the wait_any operation.  This method returns an
        ActionHandle with the results of waiting.  If None is returned
        then the ActionManager assumes that it can call this method again.
        Note that an ActionHandle can be returned with a dummy value,
        to indicate an error.
        """

        # TBD: ONLY REALLY NEED TO RETURN ANY ONE - MODIFY DISPATCHER TO RETURN THE FIRST OF ANY QUEUE THAT HAS SOMETHING.
        queues_to_check = self.client.queues_with_results()
        if len(queues_to_check) > 0:

           # this protects us against the case where we get an 
           # action handle that we didn't know about or expect.

           for queue_name in queues_to_check:

               task = self.client.get_result(override_type=queue_name)
               if task.id in self._ah:
                   ah = self._ah[task.id]
                   self._ah[task.id] = None
                   ah.status = ActionStatus.done
                   self.results[ah.id] = pickle.loads(task.result)
                   return ah
               else:
                   # TBD: WE SHOULD OBVIOUSLY DO SOMETHING ELSE HERE.
                   print("TROUBLE - GOT RESULTS WE DIDN'T EXPECT!!!")
        else:
          # if the queues are all empty, wait some time for things to fill up.
          # constantly pinging dispatch servers wastes their time, and inhibits
          # task worker communication. the good thing about queues_to_check
          # is that it simultaneously grabs information for any queues with
          # results => one client query can yield many results.
          
          # TBD: We really need to parameterize the time-out value, but it
          #      isn't clear how to propagate this though the solver manager
          #      interface layers.
          time.sleep(0.01)

if not using_pyro:
    SolverManagerFactory.deactivate('phpyro')
