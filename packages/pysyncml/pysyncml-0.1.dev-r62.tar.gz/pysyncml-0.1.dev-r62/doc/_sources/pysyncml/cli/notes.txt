.. ----------------------------------------------------------------------------
.. file: $Id$
.. auth: griffin <griffin@uberdev.org>
.. date: 2012/07/01
.. copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
.. ----------------------------------------------------------------------------

Sample Implementation: sync-notes
=================================

Below is a sample implementation of a pysyncml peer which synchronizes
notes. Notes are the most basic data type as they are a simple
octet-stream, but it is a valuable sample as it demonstrates tho
following aspects of a pysyncml client:

* Use the :class:`pysyncml.cli.DirectorySyncEngine` command-line
  interface helper class.

* Maintain local state and detecting changes.

* Support Funambol servers (which do not support hierarchical sync).

* Enable both client-side and server-side SyncML roles by subclassing
  `DirectorySyncEngine`.

Approach
--------

The `sync-notes` program maintains the synchronization of a set of
files in a given directory with a remote "Note" storage SyncML server.
When launched, it scans the directory for any changes, such as new
files, deleted files, or modified files and reports those changes to
the local :meth:`pysyncml.Context.Adapter
<pysyncml.context.Context.Adapter>`. Then, it engages in one of the
following activities:

* Describe local configurations or pending changes.

* Synchronize with a (potentially previously configured) remote SyncML
  peer.

* Launch a (potentially previously configured) server that will
  listen on an HTTP port and accept and engage in synchronization
  sessions.

Most of the structure of this functionality is implemented by the
:class:`pysyncml.cli.DirectorySyncEngine` command-line interface
helper class. Thus the ``sync-notes`` program only needs to provide
the following functionality:

* A subclass of the :class:`pysyncml.cli.DirectorySyncEngine` which
  defines some local device information and the model for how the
  state of a NoteItem, a subclass of :class:`pysyncml.Item
  <pysyncml.items.base.Item>`, is stored.

* Scanning the local directory for changes (additions, modifications
  and deletions).

* A subclass of :class:`pysyncml.Agent <pysyncml.agents.base.Agent>`,
  which provides the glue between the pysyncml Adapter and the
  peer-specific item datastore that is being synchronized.

Code
----

.. include:: notes.py
   :code: python

.. ----------------------------------------------------------------------------
.. end of $Id: README.txt 24 2012-06-19 19:35:12Z griff1n $
.. ----------------------------------------------------------------------------
