Introduction
======================

.. image:: https://drone.io/bitbucket.org/aodag/python-connpass/status.png

`connpass API <http://connpass.com/about/api/>`_

INSTALL
------------------

::

  $ pip install python-connpass

or

::

  $ easy_install python-connpass


API
-------------------

Now, connpass has one API.

- event search http://connpass.com/api/v1/event/

example::

  connpass = Connpass()
  results = connpass.search(event_id=[364])

Command
-----------------------------

::

   usage: connpass [-h] [--event-id [EVENT_ID [EVENT_ID ...]]]
                   [--keyword [KEYWORD [KEYWORD ...]]]
                   [--keyword-or [KEYWORD_OR [KEYWORD_OR ...]]]
                   [--ym [YM [YM ...]]] [--ymd [YMD [YMD ...]]]
                   [--nickname [NICKNAME [NICKNAME ...]]]
                   [--owner-nickname [OWNER_NICKNAME [OWNER_NICKNAME ...]]]
                   [--series-id [SERIES_ID [SERIES_ID ...]]] [--start START]
                   [--count COUNT] [--format {json}]
   
   optional arguments:
     -h, --help            show this help message and exit
     --event-id [EVENT_ID [EVENT_ID ...]]
     --keyword [KEYWORD [KEYWORD ...]]
     --keyword-or [KEYWORD_OR [KEYWORD_OR ...]]
     --ym [YM [YM ...]]
     --ymd [YMD [YMD ...]]
     --nickname [NICKNAME [NICKNAME ...]]
     --owner-nickname [OWNER_NICKNAME [OWNER_NICKNAME ...]]
     --series-id [SERIES_ID [SERIES_ID ...]]
     --start START
     --count COUNT
     --format {json}
