.. ----------------------------------------------------------------------------
.. file: $Id$
.. auth: griffin <griffin@uberdev.org>
.. date: 2012/07/01
.. copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
.. ----------------------------------------------------------------------------

Implementing a SyncML Client
============================

.. contents::

The general approach to implementing a SyncML client with pysyncml is
to create an agent (which interfaces with your data) and an adapter
(which will interface with the SyncML peers), connect the two, scan
the local datastore and notify the adapter of any `local` changes and
then invoke the synchronization.

For command-line interfaces, there are helper classes to make this
significantly easier to implement, by providing automatic storage
management, standard command-line options and simple server-side
support. Please see :doc:`cli/engine` for details on how to implement a
command-line interface (CLI).

Define an Agent
---------------

A pysyncml Agent is the interface between the SyncML
framework/protocol and your local data storage, and therefore is what
you, the pysyncml caller, must provide by implementing the
:class:`pysyncml.Agent <pysyncml.agents.base.Agent>` interface. At its
simplest, it must support fetching, updating, deleting and listing
items. These items must implement the :class:`pysyncml.Item
<pysyncml.items.base.Item>` interface, which essentially only means
that it provides the `id` attribute which does not have to be any
particular type, but must be convertable to a string via a call to
``str()``. For conceptual simplicity, `Item`s should also know how to
serialize/deserialize themselves, but technically this is only
required at the `Agent` interface.

The stripped-down minimal API is listed here --- see
:doc:`items/index` and :doc:`agents/index` for details:

.. code-block:: python

  import pysyncml

  class MyItem(pysyncml.Item):
    # Items must have an agent-unique ID that can be converted via `str()`
    id = ...
    # Items should be able to serialize and deserialize themselves
    def dump(self, stream, contentType=None, version=None): ...
    @classmethod
    def load(cls, stream, contentType=None, version=None): ...

  class MyAgent(pysyncml.Agent):
    # An agent must declare what content types it can de/serialize,
    # which must be a list of pysyncml.ContentTypeInfo objects.
    contentTypes = ...
    # An agent must be able to serialize and deserialize items
    def dumpItem(self, item, stream, contentType=None, version=None):
      # Usually, just invokes the item's dump method:
      return item.dump(stream, contentType, version)
    @classmethod
    def loadItem(cls, stream, contentType=None, version=None):
      # Usually, just invokes the item's load method:
      return MyItem.load(stream, contentType, version)
    # An agent must be able to list, add, fetch, modify and delete items
    def getAllItems(self): ...
    def addItem(self, item): ...
    def getItem(self, itemID): ...
    def replaceItem(self, item, reportChanges): ...
    def deleteItem(self, itemID): ...

  # Now create an instance of the agent --- note that this could
  # potentially be done at any point, not necessarily before the
  # adapter instance has been created.

  agent = MyAgent(...)

See the :class:`pysyncml.NoteItem <pysyncml.items.note.NoteItem>`
class for an example Item
implementation. :class:`pysyncml.ContentTypeInfo
<pysyncml.ctype.ContentTypeInfo>` for details on the
Agent.contentTypes objects.

Create an Adapter
-----------------

A pysyncml Adapter is the object that encapsulates the entire SyncML
interaction with a remote SyncML peer. An adapter requires several
pieces of information, such as the local devices type and
capabilities, as well as a repository to store contextual information
(using sqlalchemy_ as database abstraction engine). This is primarily
necessary so that future "update" synchronizations do not need to
re-transmit all the information, but instead do a differential sync,
which is much faster.

The stripped-down minimal API is as follows --- see :doc:`context` and
:doc:`model/adapter` for details:

.. code-block:: python

  import pysyncml

  # Create a "Context" object, which primarily tells pysyncml where to
  # store synchronization state information. In this example, the
  # storage is a sqlite file in /tmp/sync.db:

  context = pysyncml.Context(storage='sqlite:////tmp/sync.db')

  # Now create the local Adapter instance, which will (if previously
  # created, load lots of information from the storage backend):

  adapter = context.Adapter()

  # Check to see if the local device information has been set, and if
  # not, provide all relevant information (note that this should only
  # happen the first time the adapter is created):

  if adapter.devinfo is None:
    adapter.name    = 'My Example SyncML Device'
    adapter.devinfo = context.DeviceInfo(
      devID             = 'IMEI:57471724140229',
      devType           = pysyncml.DEVTYPE_SMARTPHONE,
      softwareVersion   = '0.1',
      manufacturerName  = 'Example Manufacturer, Inc.',
      modelName         = 'EX-RD42',
      # if synchronizing with funambol, add the following as funambol
      # does not support hierarchical data structures yet (as of
      # 10.0.3), such as the new OMADS 1.2.2 files and folders. A
      # future pysyncml framework work-around will allow it to
      # auto-detect this limitation.
      hierarchicalSync  = False,
      )

  # Next, check to see if the remote SyncML peer (i.e. SyncML server)
  # information has been set, and if not, provide all relevant
  # information to be able to connect to that SyncML server:

  if adapter.peer is None:
    adapter.peer = context.RemoteAdapter(
      url      = 'https://www.example.com/funambol/ds',
      auth     = pysyncml.NAMESPACE_AUTH_BASIC,
      username = 'guest',
      password = 'guest',
      )

See the :class:`pysyncml.Context <pysyncml.context.Context>`
class for details on the `Adapter` and `RemoteAdapter` methods.

.. TODO:: add reference to DeviceInfo documentation...

Connect the Adapter
-------------------

Now that the adapter is configured, it must be connected to the agent.
This is done by creating a ``Store`` which primarily provides a local
URI (relative to the adapter) that the agent is connected to. This
allows a single adapter to synchronize multiple datastores, such as
contacts, agendas and notes, all as part of the same transaction.

Currently, there is a limitation within `pysyncml` which does not
allow the registration of the same datastore multiple times, and as a
result you must first check to see if the datastore has already been
registered. In the future, this restriction will be removed:

.. code-block:: python

  # Check to see if the store with URI 'example' already exists,
  # and if so, get a reference to it, otherwise create a new Store:

  if 'example' in adapter.stores:
    store = adapter.stores['example']
  else:
    store = adapter.addStore(context.Store(
      uri         = 'example',
      displayName = 'My Local Example Datastore',
      # if synchronizing with funambol, add the following as funambol
      # does not "appreciate" a Datastore having a different maximum
      # object size than the adapter. A future pysyncml framework
      # work-around will allow it to auto-detect this limitation.
      maxObjSize  = None))

  # Then attach the agent to the adapter's store:

  store.agent = agent

Scan for Local Changes
----------------------

For adapters that have been synchronized before, you now need to
notify the adapter of any local changes (unless you don't want to
notify the server of local client modifications --- see
:ref:`section.invoke` for details):

.. code-block:: python

  # In this example, we will assume that 'MyAgent' implements a method
  # 'getAllLocalChanges()' that returns a list of lists where the
  # first element is the item, and the second element indicates how
  # the item changed, i.e. it is one of the following constants
  # defined in pysyncml:
  #   - pysyncml.ITEM_ADDED
  #   - pysyncml.ITEM_MODIFIED
  #   - pysyncml.ITEM_DELETED
  # eventually, pysyncml will support soft-deletes, in which case the
  # latter can also be pysyncml.ITEM_SOFTDELETED.

  # store.peer will be None if the adapter has no record of having
  # synchronized this datastore, in which case you do not need to scan
  # for changes since a complete non-incremental synchronization will
  # be necessary.

  if store.peer is not None:
    for item, changeType in agent.getAllLocalChanges():
      store.registerChange(item.id, changeType)

.. _section.invoke:

Invoke a Synchronization
------------------------

When the client is ready to execute a synchronization, it should call
the :meth:`pysyncml.api.Adapter.sync <pysyncml.api.Adapter.sync>`
method, which accepts several different modes to override the default:

**pysyncml.SYNCTYPE_AUTO**:

  The default sync type, which specifies that the Adapter should
  try to determine the best applicable synchronization type to apply.
  In general, this means using **pysyncml.SYNCTYPE_TWO_WAY**.

**pysyncml.SYNCTYPE_TWO_WAY**:

  The standard sync type, which allows both client and server to send
  and receive modifications. After such a sync type has completed
  successfully, both SyncML peers will have the exact same local
  datastores.

**pysyncml.SYNCTYPE_SLOW_SYNC**:

  Invoked when the SyncML peers have not synchronized before or a data
  or protocol corruption has occurred. This forces the server to
  perform an in-depth analysis of all items in both local and remote
  datastores to merge them with as few duplicates and conflicts as
  possible. As the identifier implies, the larger the dataset, the
  slower this sync type is.

**pysyncml.SYNCTYPE_ONE_WAY_FROM_CLIENT**:

  Similar to ``pysyncml.SYNCTYPE_TWO_WAY``, except only client
  modifications are sent to the server. Server modifications are
  postponed.

**pysyncml.SYNCTYPE_REFRESH_FROM_CLIENT**:

  All server items are deleted and replaced by the items in the
  client. This is generally only used when a different client is known
  to have been corrupted and accidentally synchronized with the
  server, thus potentially deleting valid data from the server. This
  mode will cause all local items to overwrite the server's items ---
  use with extreme caution.

**pysyncml.SYNCTYPE_ONE_WAY_FROM_SERVER**:

  Similar to ``pysyncml.SYNCTYPE_TWO_WAY``, except only server
  modifications are sent to the client. Client modifications are
  postponed.

**pysyncml.SYNCTYPE_REFRESH_FROM_SERVER**:

  All client items are deleted and replaced by the items in the
  server. This is generally only used when the client is known to be
  corrupted and losing any changes performed locally on the client are
  deemed insignificant --- use with caution.

The following is the most common (and recommended) form of invoking
a client-side synchronization:

.. code-block:: python

  # The following example allows the adapter to determine which
  # synchronization type to perform, which generally speaking will
  # default to two-way sync:

  adapter.sync()

Real-World Application
----------------------

Although this guide has distilled the task of creating a SyncML client
down to a few critical steps:

#. provide Agent and Item subclasses,
#. create a context and Adapter,
#. register local datastore changes, and
#. invoking the synchronization

The details, however, can get significantly more complex.

For example, a client may or may not be able to determine what local
changes have occurred since the last sync. The pysyncml framework has
no way to differentiate between a client that has no changes and a
client that cannot detect changes, so it is critical that agents in
such a scenario do **NOT** use the default sync method and instead use
the ``pysyncml.SYNCTYPE_SLOW_SYNC`` mode.

For this reason, pysyncml also provides some helper classes for
implementing a command-line SyncML peer. See :doc:`cli/engine` which
details that process as well as using the ``sync-notes`` real-world
application as an example. Although it synchronizes a relatively
simple object type (notes, which are simply an octet stream), it does
demonstrate some of the key concepts of pysyncml.

.. _sqlalchemy: http://www.sqlalchemy.org

.. ----------------------------------------------------------------------------
.. end of $Id: README.txt 24 2012-06-19 19:35:12Z griff1n $
.. ----------------------------------------------------------------------------
