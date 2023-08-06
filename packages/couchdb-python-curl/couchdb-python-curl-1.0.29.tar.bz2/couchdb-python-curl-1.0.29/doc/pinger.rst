Pinger
======

Sometimes, you need to get your CouchDB views in actual state. The only way is to call each document (one view function per document) in each databases. I called this process - "ping" (this is absolutely new word). 

Pinging CouchDB may be painful without apropriate tool. This tool is pinger (couchdb-curl-pinger in your installation).

Usage
~~~~~
::

  pinger.py [options] url1 ... urlN

  Options:

   -h, --help            show this help message and exit
   -v, --verbose         Be verbose
   -p THREADS, --threads=THREADS
                         Threads count. Defaults to CPU count
   -t TIMEOUT, --timeout=TIMEOUT
                         Script execution timeout


URL may link to:

* Document - and pinger will ping only one document. Example: http://localhost:5984/database/yourdocument

* Database - and pinger will ping whole database. Example: http://localhost:5984/database/

* Server - and pinger will ping all databases on server. Example: http://localhost:5984/

As you see above, you may limit script execution time (to safe use in your cron-scripts, without worry to forkbomb server) and limit concurrency of view requests.



Example
~~~~~~~
::

  couchdb-curl-pinger http://node1:5984/bbb http://node2:5984/bbb

Will ping all document in database bbb on hosts node1 and node2


Another example
~~~~~~~~~~~~~~~
::

  couchdb-curl-pinger -t 30 -p 2 http://node1:5984

Will ping all documents in all databases on server node1 with script execution timeout 30s in 2 concurrent threads.
