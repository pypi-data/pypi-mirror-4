.. ----------------------------------------------------------------------------
.. file: $Id$
.. auth: griffin <griffin@uberdev.org>
.. date: 2012/08/12
.. copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
.. ----------------------------------------------------------------------------

Implementing a SyncML Command-Line Interface
============================================

.. contents::

Although implementing a command-line SyncML peer with pysyncml is no
different than implementing any other pysyncml client and/or server,
the `pysyncml.cli` module provides some helper classes that simplify
the task significantly for command-line interfaces. Specifically, the
`pysyncml.cli.CommandLineSyncEngine` class provides the following
functionality out-of-the-box:

* Basic data storage/model configuration and setup.
* Simple single-user server implementation.
* Common command-line option setup, parsing and usage, including:

  * verbosity control,
  * help, configuration, and pending changes display,
  * device ID, name and label control,
  * remote URL/URI and username/password setting,
  * synchronization type, client and server modes control,
  * configuration name and location control.

Using the SyncEngine currently does imply some limitations, including:

* Only a single local datastore can be synchronized at a time.

Overview
--------

To implement a command-line program using the helper classes in
`pysyncml.cli`, you generally use one of the following approaches:

* **Directory based approach**:

  With this approach, the items being synchronized are stored in a
  directory, and different directories can have different application
  and synchronization profiles. This de-centralized method allows the
  user to have multiple directories that represent "units of content";
  the directory can be moved around as long as it and all of its
  contents remains together and intact.

  This approach is implemented by subclassing
  :class:`pysyncml.cli.DirectorySyncEngine
  <pysyncml.cli.base.DirectorySyncEngine>`.

* **Local-user based approach**:

  A more centralized approach, where the items being synchronized are
  stored in some host-local per-user location that may or may not be a
  file-based location. In this case, the user must specifically
  request a different configuration in order to choose a different
  synchronization profile. For example, this could be used when
  synchronizing the settings of another application that are stored in
  a pre-defined user-specific directory, such as
  "~/.config/libreoffice".

  This approach is implemented by subclassing
  :class:`pysyncml.cli.LocalUserSyncEngine
  <pysyncml.cli.base.LocalUserSyncEngine>`.

Once the right approach is found, then the following steps are required:

#. :ref:`extend`:

   Subclass the appropriate `SyncEngine` implementation and add any
   relevant hooks.

#. :ref:`agent`:

   Provide a :class:`pysyncml.Agent <pysyncml.agents.base.Agent>`
   implementation, which primarily exposes CRUD access to your data.

#. :ref:`invoke`:

   Invoke your `SyncEngine`'s `run()` method and tie in execution
   entrypoints.

.. _extend:

Subclass a SyncEngine
---------------------

The base class `CommandLineSyncEngine` constructor accepts several
parameters which control the profile of the SyncML adapter. These
parameters are typically only used as *default* parameters, when
they cannot be loaded from a previous call to the engine.

The following example illustrates a typical subclass of the
directory-based approach:

.. code-block:: python

  import sqlalchemy as sa
  import pysyncml
  import pysyncml.cli

  class MySyncEngine(pysyncml.cli.DirectorySyncEngine):

    def __init__(self):
      super(NotesEngine, self).__init__(
        appLabel          = '...',           # a short label used to identify this program
        appDisplay        = '...',           # a user-friendly title of this program
        devinfoParams     = dict(...),       # default local device information
        storeParams       = dict(...),       # default local datastore information
        agent             = MyAgent(self),   # a reference to the local Agent
        )

    @pysyncml.cli.hook('model.setup.extend')
    def _createDataItemModel(self):
      # extend the self.model to include any persistent data objects that
      # this engine requires to maintain state, using the self.model.DatabaseObject
      # SQLAlchemy declarative_base class as a base class. an example:
      class MyDataItem(self.model.DatabaseObject):
        # NOTE: an `id` attribute (a UUID string) is provided by the ORM
        data = sa.Column(sa.Text)
      self.model.MyDataItem = MyDataItem

    @pysyncml.cli.hook('adapter.create.store')
    def _scanDataItems(self, context, adapter, store):
      # adding a hook to when the pysyncml store is created to detect changes
      # in the local datastore and register them on the store, for example:
      self.agent.scan(store)

The following table details all the hooks that are available and when
they are called. In general, they fall into one of four categories:

* `options.setup`:

  These are called once during program initialization to setup the
  options that this program can accept on the command line.

* `options.parse`:

  These are called once during program start-up to parse the options
  specified on the command line and to do preliminary SyncEngine
  configuration. The options are actually parsed twice: once to
  determine the data directory, and a second time within the context
  of the data directory.

* `options.persist`:

  These hooks are called to affect the serialization and
  de-serialization of options to the data directory so that
  appropriate data defaults can be persisted.

* `model.setup`:

  These are called once after program start-up to configure the
  program's data model, check the integrity of the database and any
  schema versioning, and apply any data migrations if needed.

  TODO: integrity checking, schema versioning and data migrations are
  not implemented yet.

* `adapter.create`:

  These are called any time the SyncEngine needs a SyncML Adapter.
  Generally speaking, in client-mode they will be called once when
  starting the transaction with a remote peer and in server-mode, they
  will be called for every request from the client (note that there
  will be multiple requests were synchronization session).

========================== ========================== =============================================
Hook                       Parameters                 Description
========================== ========================== =============================================
options.setup.init         (none)                     Called when the ArgumentParser has
                                                      been created (and stored in
                                                      ``self.parser``), but no options
                                                      have been added yet.
options.setup.generic      (none)                     Called after common command-line
                                                      options have been added (such as
                                                      ``--verbose``), but before
                                                      SyncEngine specific options have
                                                      been added to ``self.parser``
                                                      (such as ``--remote-uri``).
options.setup.term         (none)                     Called after all options have been
                                                      added to the ArgumentParser in
                                                      ``self.parser``, but before the
                                                      options are parsed.
options.parse.init         (none)                     Called just before the ArgumentParser's
                                                      ``parse_args()`` method is called for
                                                      the first time.
options.parse.datadir      (none)                     Called immediately after the first
                                                      call to ``parse_args()``, to establish
                                                      the data directory. The SyncEngine
                                                      expects ``self.dataDir`` to point
                                                      to a directory that can be used to
                                                      persist data to. Typically, this is
                                                      taken care of by an existing subclass
                                                      of `CommandLineSyncEngine`.
options.parse.term         (none)                     Called just after the ArgumentParser's
                                                      ``parse_args()`` method is called,
                                                      and before the logging is configured
                                                      as specified in the command-line
                                                      options. The results of the parse
                                                      are available in ``self.options``
                                                      (parameters) and in ``self.args``
                                                      (arguments).
options.persist.load       option-dictionary          Called after the first call to
                                                      ``parse_args()`` and after any persisted
                                                      values stored in the passed-in dictionary
                                                      have been applied to the parser. This
                                                      hook can then do any "clean-up" if
                                                      necessary.
options.persist.save       option-dictionary          Called after all options have been
                                                      processed and all `options.parse.*`
                                                      hooks have been called. The passed-in
                                                      dictionary should be modified to store
                                                      any key-value pairs that, upon
                                                      deserialization, will be provided to
                                                      ``self.parser.set_defaults()``.
model.setup.init           (none)                     Called after logging is setup, the
                                                      database backend engine has been
                                                      created (and stored in
                                                      ``self.dbengine``), and the database
                                                      session is created (and stored in
                                                      ``self.dbsession``), but before the
                                                      any models or database objects are
                                                      created.
model.setup.extend         (none)                     Called after the SyncEngine data
                                                      model has been created (and stored
                                                      in ``self.model``), but before any
                                                      tables are created (if needed) or
                                                      model versions are checked. This is
                                                      the most common hook to bind to:
                                                      this is where the application will
                                                      add any models that it needs to
                                                      manage the datastore state.
model.setup.term           (none)                     Called after the database integrity
                                                      is checked, model versions are
                                                      checked and any data migrations are
                                                      applied.
adapter.create.init        (none)                     Called when a SyncEngine needs an
                                                      Adapter, but before anything is
                                                      actually done.
adapter.create.context     context                    Called after a `pysyncml.Context`
                                                      object is created. Note that the
                                                      context is never made into an
                                                      attribute of ``self``, and is why
                                                      it is passed in as a parameter to
                                                      the hook function.
adapter.create.adapter     context, adapter           Called after a `context.Adapter`
                                                      is either loaded from the database
                                                      or initialized based on the command
                                                      line options. Both the context and
                                                      the resulting adapter are provided
                                                      as hook parameters.
adapter.create.peer        context, adapter, peer     Called after the remote peer is
                                                      loaded from the database or
                                                      initialized based on the command
                                                      line options. Note that this hook
                                                      will *only* be called when running
                                                      in client-mode.
adapter.create.store       context, adapter, store    Called after the `self.model.Store`
                                                      is loaded from the database or
                                                      initialized based on the command
                                                      line options. This hook is
                                                      typically used to then scan for
                                                      changes in the local datastore and
                                                      register them to the `Store`. This
                                                      will be called before any local
                                                      pending changes are reported to
                                                      the user (if requested).
adapter.create.term        context, adapter           Called after the context, adapter,
                                                      peer, and store are completely
                                                      ready for synchronization, but
                                                      before they are passed back to
                                                      the SyncEngine for consumption.
describe                   stream                     Called when a `describe` operation
                                                      is requested. This is called after
                                                      the engine and adapters have displayed
                                                      their configuration description. The
                                                      `stream` is a file-like object where
                                                      program-specific descriptions should
                                                      be sent to via ``stream.write(...)``.
========================== ========================== =============================================

.. _agent:

Implement an Agent
------------------

The `pysyncml.Agent` provides the binding between the pysyncml SyncML
synchronization engine and your data. As pysyncml treats your data as
opaque objects, you need to implement all CRUD operations and a
limited set of other optional functions (especially when handling
hierarchical data).

A stripped-down minimal API with typical functionality follows --- see
:doc:`../agents/index` for details:

.. code-block:: python

  import pysyncml

  class MyAgent(pysyncml.Agent):

    # An agent must declare what content types it can de/serialize,
    # which must be a list of pysyncml.ContentTypeInfo objects.
    contentTypes = [ pysyncml.ContentTypeInfo('text/plain', 1.0, preferred=True) ]

    # The above MySyncEngine called the Agent constructor with itself
    def __init__(self, engine, *args, **kw):
      super(MyAgent, self).__init__(*args, **kw)
      self.engine = engine

    # An agent must be able to serialize and deserialize items
    def dumpItem(self, item, stream, contentType=None, version=None):
      # Usually, just invokes the item's dump method (if it has one):
      return item.dump(stream, contentType, version)

    def loadItem(self, stream, contentType=None, version=None):
      # Usually, just invokes the item's load method (if it has one):
      return self.engine.model.MyDataItem.load(stream, contentType, version)

    # An agent must be able to list, add, fetch, modify and delete items
    def getAllItems(self): ...
    def addItem(self, item): ...
    def getItem(self, itemID): ...
    def replaceItem(self, item, reportChanges): ...
    def deleteItem(self, itemID): ...

    # If an agent will also support matching, merging and conflict resolution
    # (only used when run as server), then it must also implement mergeItems,
    # and optionally matchItems (to make it more efficient than the default
    # implementation).
    def mergeItems(self, localItem, remoteItem, changeSpec): ...
    def matchItem(self, item): ...

.. _invoke:

Launch the SyncEngine
---------------------

This is the easy part... cut-n-paste the following to make your python
file executable as well as providing a ``main`` entrypoint (which can
be used in the ``entry_points`` definition of your ``setup.py``
file):

.. code-block:: python

  def main(argv=None):
    engine = MySyncEngine()
    return engine.configure(argv).run()
  if __name__ == '__main__':
    sys.exit(main())


Example Implementation
----------------------

See :doc:`notes` for an example of a real-world program provided by
the pysyncml package that uses the `pysyncml.cli` functionality.

.. ----------------------------------------------------------------------------
.. end of $Id$
.. ----------------------------------------------------------------------------
