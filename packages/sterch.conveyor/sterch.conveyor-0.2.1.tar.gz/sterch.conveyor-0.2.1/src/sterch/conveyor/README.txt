---------------------
 General description
---------------------

Package is used for simultaneous tasks processing by conveyor.

         Inital stage               Stage #2            ...     Stage #N          Final Stage
-------------------------+---------------------------+----------------------+----------------------------  
Initial workers   -> Queue #1 <->  Workers #1  <-> Queue #2 <-> .... <-> Queue #N -> Final workers
(put tasks into                   middle tasks                                       tasks postprocessing
   a queue)                       processing                                         (output, DB, CSV, GET/POST, 
   etc.)
-------------------------+---------------------------+----------------------+-----------------------------

Tasks processing is divided into stages. Every stage (except for two special stages 
initial and final) has:
 * an input tasks queue
 * an output tasks queue
 * delay for getting/putting tasks
 * certain amount of identical workers which get tasks from the input queue and put one or more
   results to the output queue. Results on the (N)th stage are input tasks for the (N+1)th stage 

There are two special stages:
 * initial stage: just generates tasks; it has no input queue.
 * final stage: just post-processes and probably outputs results; it has no output queue.

Tasks processing by workers is simultaneous. 

Workers could be defined by their activity function. It is simply generator that gets 
one task as input and yields a sequence of results. 

Optionally an event could be defined for a stage to synchronize the conveyor 
with other application threads.

 ---------------
 ZCML directives
 ---------------
 They are defined within the namespace http://namespaces.sterch.net/conveyor
 
<conveyor name="Conveyor #1">

	<init_stage
		name="Initial stage"           # Stage name.
		activity = "callable"          # Python callable object identifier.
		                               # Usually this is a generator.
		quantity = "50"				   # Number of concurrent workers that does the activity
		delay = "5"                    # Delay for getting/putting tasks     
		out_queue = "out-queue-name"   # IQueue (see sterch.queue) utility name to output tasks
		event = "event-name"/>         # Optional IEvent (see sterch.threading) utility name.


	<stage
		name="Regular stage"
		activity = "callable"
		quantity = "50"
		in_queue = "in-queue-name"
		out_queue = "out-queue-name"
		delay = "5"
		event = "event-name" />

	<final_stage
		name="Final stage"
		activity = "callable"
		quantity = "50"
		in_queue = "in-queue-name"
		delay = "5"
		event = "event-name"/>

</conveyor>

It is possible to define as many stages as you need.
Conveyor loops, unreachable final state, missing initial stage are not allowed.

--------
Examples
--------
See package tests.

--------
Comments
--------
Send all your comments on the package to Maksym Polshcha (maxp@sterch.net)