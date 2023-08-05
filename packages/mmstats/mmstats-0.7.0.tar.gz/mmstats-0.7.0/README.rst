`Documentation <http://mmstats.readthedocs.org/>`_ |
`Package <http://pypi.python.org/pypi/mmstats>`_ |
`Code <http://github.com/schmichael/mmstats/>`_

.. image:: https://secure.travis-ci.org/schmichael/mmstats.png?branch=master
   :target: http://travis-ci.org/schmichael/mmstats/


=====
About
=====

Mmstats is a way to expose and read diagnostic values and metrics for
applications.

Think of mmstats as /proc for your application and the readers as procps
utilities.

This project is a Python implementation, but compatible implementations can be
made in any language (see Goals).

Discuss at https://groups.google.com/group/python-introspection

-----
Goals
-----

* Separate publishing/writing from consuming/reading tools
* Platform/language independent (a Java writer can be read by a Python tool)
* Predictable performance impact for writers via:

  * No locks (1 writer per thread)
  * No syscalls (after instantiation)
  * All in userspace
  * Reading has no impact on writers

* Optional persistent (writer can sync anytime)
* 1-way (Publish/consume only; mmstats are not management extensions)

=====
Usage
=====

------------
Requirements
------------

CPython 2.6 or 2.7 (Windows is untested)

PyPy (only tested in 1.7, should be faster in 1.8)

-----
Using
-----

1. ``python setup.py install``
2. ``import mmstats``
3. Create a subclass of mmstats.MmStats like:

::

    class WebStats(mmstats.MmStats):
        status2xx = mmstats.CounterField(label='status.2XX')
        status3xx = mmstats.CounterField(label='status.3XX')
        status4xx = mmstats.CounterField(label='status.4XX')
        status5xx = mmstats.CounterField(label='status.5XX')
        last_hit = mmstats.DoubleField(label='timers.last_hit')

4. Instantiate it once per process: (instances are automatically thread local)

::

    webstats = WebStats(label_prefix='web.stats.')

5. Record some data:

::

    if response.status_code == 200:
        webstats.status2xx.inc()

    webstats.last_hit = time.time()

6. Run ``slurpstats`` to read it
7. Run ``mmash`` to create a web interface for stats
8. Run ``pollstats -p web.stats.status 2XX,3XX,4XX,5XX /tmp/mmstats-*`` for a
   vmstat/dstat like view.
9. Did a process die unexpectedly and leave around a stale mmstat file?
   ``cleanstats /path/to/mmstat/files`` will check to see which files are stale
   and remove them.
