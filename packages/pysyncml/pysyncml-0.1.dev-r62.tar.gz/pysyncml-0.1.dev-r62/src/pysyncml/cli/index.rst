.. ----------------------------------------------------------------------------
.. file: $Id$
.. auth: griffin <griffin@uberdev.org>
.. date: 2012/07/01
.. copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
.. ----------------------------------------------------------------------------

Command-Line Programs
=====================

.. contents::

The `pysyncml` package comes with several command-line programs that
can be used both as clients and as servers. Each program is documented
here, however, they all share a significant amount of common
functionality which is documented in :ref:`section.common`.

Note Synchronizer: ``sync-notes``
---------------------------------

The ``sync-notes`` command line program allows notes to be stored in a
directory, one note per file, and to synchronize them with a SyncML
peer that supports the de-facto "note" datatype, i.e. one of the
following content-types:

* ``text/plain``
* ``text/x-s4j-sifn``

In the case of ``text/plain``, no information beyond the file contents is
synchronized and therefore remote peers will need to somehow generate
the filename (typically either by using a numeric ID or by using the
first line of the note).

In the case of ``text/x-s4j-sifn``, both the contents and the filename
(stored in the "Subject" field) are synchronized. Unfortunately some
SyncML servers (specifically, funambol) will override the filename
with a generated value.

All files in the specified directory, including subdirectories, will
be targeted for synchronization, with the exception of the ".sync"
directory, where sync-notes stores its state. If sync-notes gets into
a bad state, the ".sync" directory and its contents can be deleted,
and the next time a full "slow-sync" synchronization will be executed.

In addition to all the :ref:`section.common`, this program also
supports the following options:

* ``-F``, ``----no-filename-sync``:

  By default, a change in a note's filename will cause the item to be
  synchronized, even if there was no change to the content. This
  option overrides this behavior to only synchronize filename changes
  if there are also content changes (this is primarily useful to
  reduce the overhead when synchronizing with a peer that does not
  properly support filename synchronization, such as funambol).


File Synchronizer: ``sync-files``
---------------------------------

The ``sync-files`` command is not yet operational.

.. TODO .. enable & complete this when sync-files works.
.. The ``sync-files`` command line program allows a file and folder
.. hierarchy to be stored in a directory and synchronized with a SyncML
.. peer that supports the SyncML standard OMADS "File" and "Folder"
.. specification, i.e. the following content-types:
.. 
.. * ``application/vnd.omads-folder``
.. * ``application/vnd.omads-file``


.. _section.common:

Common Options
--------------

In general, the command-line programs provided with pysyncml
synchronize files that are stored in a particular directory, with each
file representing a SyncML object. The content of the file depends on
which program is invoked --- see the details in the relevant section
above.

The programs are capable of running in client mode (the default) or in
server mode (with the ``--server`` option). Currently a single
directory should only be used for one of the other, not both.

Example first-time synchronization of a directory as a client::

  $ PROGRAM --remote https://example.com/funambol/ds \
            --username USERNAME --password PASSWORD \
            DIRECTORY

Follow-up client-mode synchronizations::

  $ PROGRAM DIRECTORY

Example first-time synchronization of a directory as a server (listen
port defaults to port 80)::

  $ PROGRAM --server --listen 8080 DIRECTORY

Follow-up server-mode synchronizations::

  $ PROGRAM DIRECTORY

(The fact that the program was run as a server the last time will
be remembered and all server settings re-applied.)

For the full documentation of all options from the command line, use::

  $ PROGRAM --help

Although ``--help`` is the best way to get the latest, most up-to-date
information about what options are available for any given program,
here is a description of all known generic options that are common to
all pysyncml command-line programs. The first set apply to both
server-side and client-side operating modes.

* ``-h``, ``--help``:

  Display a help summary and option list.

* ``-v``, ``--verbose``:

  Causes the program to output more messages -- this option can be
  specified multiple times to progressively increase the verbosity,
  with five being the most verbose level.

* ``-q``, ``--quiet``:

  Normally, at the end of the synchronization, a summary of all
  activity is displayed, regardless of the level of verbosity. This
  option suppresses the summary display only (see below for a
  description of this summary).

* ``-d``, ``--describe``:

  Startup the program as normal, but before any synchronization is
  actually performed (either as client or as a server), display a full
  description of the current configuration as well as anything that is
  currently known about the remote peer(s).

* ``-l``, ``--local``:

  Display any pending local changes and exit before any
  synchronization is performed.

* ``-i``, ``--id`` *ID*:

  Override the default device ID for the local peer. Normally, on
  first invocation, a unique device ID is generated (based on program
  name, local MAC address and current time) and saved. On subsequent
  invocations, the stored value is retrieved and used.

  NOTE: TODO: currently, if trying to override a previously stored ID
  (i.e. to change a current value), it is safest to delete the entire
  ".sync" directory and restart synchronization with a "slow-sync".

* ``-n``, ``--name`` *NAME*:

  Set the local adapter/store name (the default is program-specific
  and usually resembles the program name).

* ``-u``, ``--username`` *USERNAME*:

  Specifies the username to perform authorization under, specifically:

  In client-mode, specifies the username to log in with.

  In server-mode, specifies the expected username that connecting
  clients must provide the credentials for to be authorized to
  synchronize with this server.

* ``-p``, ``--password`` *PASSWORD*:

  Used in conjunction with ``--username``:

  In client-mode, specifies the username's password to log in with.

  In server-mode, specifies the expected password that connecting clients
  must use to be authorized to synchronize with this server.

  In either case, if ``--username`` is specified, but ``--password`` is
  not, it will be prompted for from the terminal. This is the recommended
  approach as it avoids leaking the password into the local hosts
  environment which, on some systems, can be compromised by other users
  on the same machine.

The following options apply only when operating in client-mode:

* ``-m``, ``--mode`` *MODE*:

  Set the requested synchronization mode - can be one:

    :sync:         normal, two-way differential synchronization.
    :full:         a complete re-synchronization from scratch.
    :pull:         download remote changes only.
    :push:         upload local changes only.
    :pull-over:    download remote changes, deleting all local data first.
    :push-over:    upload local changes, deleting all remote data first.

* ``-r``, ``--remote`` *URL*

  Specifies the URL of the remote SyncML synchronization server ---
  only required if the target directory has never been synchronized,
  or the synchronization meta information was lost.

* ``-R``, ``--remote-uri`` *URI*:

  Specifies the remote URI of the datastore to synchronize with. If
  left unspecified, pysyncml will attempt to identify it automatically
  by selecting the best-matching content-types. The latter method is
  the preferred approach, and should only be overriden if it
  misbehaves.

  NOTE: TODO: overriding the automated association is currently not
  implemented.

The following options apply only when operating in server-mode:

* ``-s``, ``--server``:

  Enables server mode (implied if ``--listen`` is specified).

* ``-L``, ``--listen`` *PORT*:

  Specifies the port to listen on for server mode (implies ``--server``
  and defaults to port 80).

* ``-P``, ``--policy`` *POLICY*:

  Specifies the conflict resolution policy that the server should use
  to resolve conflicts that cannot be merged or otherwise resolved --
  can be one of "error" (the default), "client-wins" or "server-wins".

As stated before, it is not recommended that the same directory be used
in both client *and* server mode.

When a command line program is invoked without the ``--quiet`` flag, a
summary report is displayed that will look something like the
following::

  +---------------------------------------------------------------------+
  |                       Synchronization Summary                       |
  +--------+------+-----------------------+-----------------------+-----+
  |        |      |         Local         |        Remote         |     |
  | Source | Mode | Add | Mod | Del | Err | Add | Mod | Del | Err | Con |
  +--------+------+-----+-----+-----+-----+-----+-----+-----+-----+-----+
  |  notes |  <>  |   2 |  11 |  -  |  -  |  -  |  -  |   4 |  -  |  -  |
  +--------+------+-----+-----+-----+-----+-----+-----+-----+-----+-----+
  |               13 local changes and 4 remote changes.                |
  +---------------------------------------------------------------------+

The summary report details all of the changes (additions,
modifications and deletions), errors and conflicts that occured broken
down by datastore (the "Source") and on which peer (local or
remote). The "Mode" column indicates what kind of synchronization mode
was selected for the given datastore and can have one of the following
meanings:

  :``SS``: Slow-sync
  :``<>``: Two-way sync
  :``->``: One-way from client to server
  :``=>``: Refresh from client to server
  :``<-``: One-way from server to client
  :``<=``: Refresh from server to client

.. ----------------------------------------------------------------------------
.. end of $Id: README.txt 24 2012-06-19 19:35:12Z griff1n $
.. ----------------------------------------------------------------------------
