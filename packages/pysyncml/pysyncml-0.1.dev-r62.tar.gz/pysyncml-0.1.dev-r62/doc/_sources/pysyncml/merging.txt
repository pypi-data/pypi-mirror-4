.. ----------------------------------------------------------------------------
.. file: $Id$
.. auth: griffin <griffin@uberdev.org>
.. date: 2012/08/28
.. copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
.. ----------------------------------------------------------------------------

Matching, Merging, and Conflict Resolution
==========================================

In an ideal world, SyncML peers would instantly synchronize globally
whenever a change occurred on any client. This would mean that
regardless of which device was accessing, displaying, and modifying
data, it would always be the most recent version. In the real world,
however, this rarely happens and certainly cannot be depended
on. Instead, devices lose network connectivity, some devices may not
auto-synchronize when there are pending changes, bugs cause
synchronization software to fail and other conditions may arise that
result in changes being made to distributed data that is
out-of-sync. When changes are made to the exact same item, we have a
SyncML **conflict**.

Certain kinds of conflicts can be resolved by the SyncML framework,
others require a *merging* of the changes by the agent, and finally
some kinds of changes cannot be automatically resolved at all.

There are two conditions in which the SyncML protocol can result in
the necessity to merge items:

* Matching items during a slow-sync:

  When two SyncML peers synchronize for the first time, they engage in
  a so-called "slow-sync", where all items are sent to the server,
  which then analyzes them and attempts to establish a common baseline
  of synchronized items. In this process, the server will attempt to
  match identical items and not duplicate them. See Matching_ for
  details.

* Concurrent changes made to the same item:

  When two SyncML peers that have synchronized before make changes to
  the same item, and then synchronize, the two items will be in a
  conflict state. Many kinds of changes are mergeable and pysyncml
  tries to identify and execute on these situations. See Conflicts_
  for details.

In either situation, pysyncml (when operating as the server) will call
on special :class:`pysyncml.Agent <pysyncml.agents.base.Agent>`
methods to help negotiate the resolution - without these methods,
pysyncml will err on the side of caution and will not automatically
take any action that may result in the loss of data unless specified
by the conflict resolution policy, see Conflicts_ for details.

Matching
--------

The first time two SyncML peers synchronize, the pysyncml framework
(when operating as the server role), will try to avoid duplicating
items by associating matching items. It does this by first calling
:meth:`pysyncml.Agent.matchItem
<pysyncml.agents.base.Agent.matchItem>` on an item (coming from the
remote peer) being synchronized. If this yields an object, then it is
compared using ``cmp()``. If that comparison returns 0 (i.e. they are
identical), then the two objects are assumed to be identical and are
associated with each other and will by synchronized normally going
forward.

If ``cmp()`` results in a non-zero value, then the items are assumed
to represent the same item, but in different states or having
different sub-properties. In this scenario, pysyncml will then call
:meth:`pysyncml.Agent.mergeItems
<pysyncml.agents.base.Agent.mergeItems>` to merge the state from the
remote peer's item into the local item. If, for any reason, the two
items cannot be merged, then a `pysyncml.ConflictError` should be
raised. When that happens, pysyncml will duplicate the items, and it
is up to the user to perform a manual merge.

An example of when matched items may need to be merged: in the context
of a contact manager, two devices may manage different aspects of the
same contact: a phone may only store the telephone numbers and an
address labeling device may only store addresses. As a result,
pysyncml can be used to match the items on both devices using the
contact name, and the server agent will then merge the phone numbers
and the address into a single contact without duplication.

Conflicts
---------

When two SyncML peers make changes to the same object without first
synchronizing the object, there ensues a conflict. It is the SyncML
peer that is operating as the server role that assumes the
responsibility for managing such a conflict. Please note that change
management and conflict resolution are difficult concepts to master,
especially in distributed environments! For this reason, do not
hesitate to ask questions on the pysyncml discussion forum if the
following documentation is not clear!

The pysyncml server framework will first attempt to merge such
conflicts (see below for details on how this is accomplished), then
allow the agents to attempt a merge, and failing that, will take one
of the following actions, based on the `conflictPolicy` setting (which
can be set on a per-datastore basis as well as a default policy for
the adapter):

* **pysyncml.POLICY_ERROR**:

  The conflict will result in a terminal error, from which the
  pysyncml server will not be able recover. It is up to the client to
  remove the conflicting change and re-synchronize, or for the
  server's `conflictPolicy` to be updated. This is the default policy.

* **pysyncml.POLICY_CLIENT_WINS**:

  The conflict is resolved by ignoring the change on the server and
  overriding it with the change from the client.

* **pysyncml.POLICY_SERVER_WINS**:

  The conflict is resolved by ignoring the change from the client and
  overriding it with the change on the server.

Merging with pysyncml
---------------------

Matching, conflict resolution and merging are only performed by the
server-side of a SyncML synchronization. When using pysyncml for the
server implementation, the pysyncml.Agent provided by the calling
environment must therefore be prepared to assist in this
process. Although it is possible for the agent to not provide any
merging functionality whatsoever, this is not recommended as it means
that very limited conflict resolution will be possible.

To help in the process of conflict resolution, the agent must
primarily help in the merging of modifications made to the same object
-- all other conflicting changes (such as simultaneous deletion and
modification of the same object) are usually handled by the
framework. The pysyncml framework helps agents with this merging by
providing two features:

* When an `Agent.replaceItem()` call is made and the flag
  `reportChanges` is set to True, then the framework will
  expect a "change-spec" to be returned.

* When an `Agent.mergeItems()` is called, it will be provided an
  aggregation of all of the "change-spec"s that have accumulated since
  the last sync and are applicable to the current merging.

These "change-specs" are opaque strings that are agent-specific and
should describe how the item was changed such that a merging of
changes to unrelated sections of the item can be merged. With the
exception that multiple change-specs are concatenated with a semicolon
(";") as delimiting separator, the pysyncml framework treats these
change-specs as opaque strings. Because of this, each agent is free to
implement them as needed.

However, pysyncml does provide many helper classes to help with
generating, parsing and applying change-spec strings, which is the
recommended approach. Here follows a discussion of how to use the most
common helper, the :class:`pysyncml.CompositeMergerFactory
<pysyncml.change.merger.CompositeMergerFactory>`. If for any reason
you need access to lower-level API's, please see the more detailed
discussion on `Merging Helpers`_, `Change Tracking Helpers`_, and
`Change-Spec Details`_ sections.

The most common SyncML item merging requirements can usually be
handled by the :class:`pysyncml.CompositeMerger
<pysyncml.change.merger.CompositeMerger>`. This class assumes that any
given changes to an item can be broken down to changes to an
independent set of fields, each of which can have different merging
strategies. The `CompositeMergerFactory` is given a dictionary of
which Merger to use for which field as well as a default merger for
all unspecified fields. Currently, there exist the following types of
mergers that can be used for this purpose:

* :class:`pysyncml.AttributeMerger <pysyncml.change.merger.AttributeMerger>`:

  which is used for atomic string-based fields, where it is assumed
  that any change to that field cannot be merged with another change
  to the exact same field.

* :class:`pysyncml.TextMerger <pysyncml.change.merger.TextMerger>`:

  which is used for text, i.e. sequences of words or lines, where
  multiple changes to the same field can be merged as long as they
  occur in different parts of the text.

An example of the "atomic" fields would be a contact's phone number. If
the number is changed from "555-1212" to "555-*9999*" on one client and
to "*111*-1212" on another, it is unlikely that a merging of these two
changes (e.g. "111-9999") would result in the desired behavior.

An example of the "non-atomic" field would be a contact's "comments"
field, where the user could add multiple lines of free-form text. In
that case, changes made to different parts of the comments may be
merged. For example, if the comments for a fictional contact "Lionel"
starts out with::

  Lionel's sister went to some boarding school.
  He owes me $150.00 (car rental).

Then, on one client, the comments' first line is modified, as
follows::

  Lionel's sister went to the "The Governor's Academy" boarding school.
  He owes me $150.00 (car rental).

And on another client, the second line is modified, as follows::

  Lionel's sister went to some boarding school.
  He owes me $50.00 (car rental - paid back $100 in August).

Then, since neither change is to the same line, the changes could be
merged together to yield::

  Lionel's sister went to the "The Governor's Academy" boarding school.
  He owes me $50.00 (car rental - paid back $100 in August).

The following example agent demonstrates the code that would be used
to implement these two examples with an item that has a "phone" and a
"comments" attribute. The "phone" attribute is an atomic field and the
"comments" attribute is a multi-line text field:

.. code-block:: python

  import pysyncml

  class MyAgent(pysyncml.Agent):

    def __init__(self, ...):

      ...

      # construct a composite merger factory that uses an AttributeMerger for
      # all attributes except the "comments" field, which uses a TextMerger (in
      # mult-line mode). note that the "default" is redundant here since the
      # AttributeMerger is the fallback default if not specified.

      self.mergerFactory = pysyncml.CompositeMergerFactory(
        default  = pysyncml.AttributeMergerFactory(),
        comments = pysyncml.TextMergerFactory())

    ...

    def replaceItem(self, item, reportChanges):

      current = self.getItem(item.id)
      cspec   = None

      if reportChanges:
        merger = self.mergerFactory.newMerger()
        merger.pushChanges('phone', current.phone, item.phone)
        merger.pushChanges('comments', current.comments, item.comments)
        cspec = merger.getChangeSpec()

      # here, the local item would get updated with the new values
      ...

      return cspec

    def mergeItems(self, localItem, remoteItem, changeSpec):

      merger  = self.mergerFactory.newMerger(changeSpec)
      tmpItem = localItem.clone()

      # the following calls to mergeChanges() will raise a ConflictError if
      # there are unmergeable changes.

      tmpItem.phone    = merger.mergeChanges('phone', localItem.phone, item.phone)
      tmpItem.comments = merger.mergeChanges('comments', localItem.comments, item.comments)

      return self.replaceItem(tmpItem, True)


Merging Helpers
---------------

Although the CompositeMerger is flexible enough to handle a very
diverse set of requirements, there are inevitably scenarios that
require more control. For those situations, it is possible to bypass
the CompositeMerger and use lower-level APIs to manage changes and
perform merges. The following sections document these APIs.

The :class:`pysyncml.Merger <pysyncml.change.merger.Merger>`
sub-classes are designed to opaquely generate and apply change-specs
to several different situations:

* :class:`pysyncml.Merger <pysyncml.change.merger.Merger>`:

  The base class for all mergers -- generally not directly useful, as
  it is primarily intended to be useful for aggregate merger
  factories, such as the :class:`pysyncml.CompositeMergerFactory
  <pysyncml.change.merger.CompositeMergerFactory>`.

* :class:`pysyncml.AttributerMerger <pysyncml.change.merger.AttributeMerger>`:

  Tracks changes to, and merges change-specs into, independent fields
  of an item. The merger expects the values to be strings.

* :class:`pysyncml.TextMerger <pysyncml.change.merger.TextMerger>`:

  Used with text-based content, either single-line or multi-line
  sequences. In single-line mode, changes are tracked with word-level
  granularity. In multi-line mode, changes are tracked with line-level
  granularity, which means that changes to the same line of the text
  will conflict and will not be auto-mergeable.

The `TextMerger` implements the entire process of comparing and
merging blocks of text and uses the `ListChangeTracker` (see below)
under the hood to keep track of these changes and detect conflicts. It
can be used either with items that are entirely composed of a single
text block (notes, for example), or with individual fields within an
item that are text blocks (for example, a "comments" field in a
contact), and is then usually combined with the `CompositeMerger`.

All of the `Merger` subclasses rely on having access to the entire
field value to simplify change detection and merge application. This
is not always feasible, for example when dealing with multi-terabyte
files, and in such scenarios it may be necessary to use the `Change
Tracking Helpers`_, which is what the mergers use under the hood.

Change Tracking Helpers
-----------------------

The change tracking helpers provided by pysyncml offer low-level
control over the generation, parsing, and utilization of change-specs.
Unlike the `Merging Helpers`_, the change tracking family of objects
typically do not require the complete value of a field. Instead, they
can be given the MD5 checksum of a field, which is most useful when
the field values are very large or otherwise not accessible.

The following change trackers exist:

* :class:`pysyncml.ChangeTracker <pysyncml.change.tracker.ChangeTracker>`:

  The base class for all low-level change-spec management classes.

* :class:`pysyncml.AttributeChangeTracker <pysyncml.change.tracker.AttributeChangeTracker>`:

  A change tracker that manages changes made to key-value based,
  independent attributes. For example, the attributes of a contact,
  such as "firstname", "lastname", etc.

* :class:`pysyncml.ListChangeTracker <pysyncml.change.tracker.ListChangeTracker>`:

  A change tracker that manages changes to an ordered sequence of
  values, where each element in that order can be added, modified
  or deleted atomically. An example application of this tracker is
  when detecting and merging changes to text blocks: when text is
  broken down into lines (in multi-line mode) or into words (in
  single-line mode).

These change trackers expose the following functionality:

* Generating and parsing change-spec strings.
* Appending a change, and collapsing multiple change-specs together.
* Change collision detection.

An example usage of the AttributeChangeTracker: assuming that fields
within an item are completely independent and that the item exposes a
dict-like interface to the attributes, then the agent's `mergeItems()`
could look something similar to:

.. code-block:: python

  class MyAgent(pysyncml.Agent):

    ...

    def mergeItems(self, localItem, remoteItem, changeSpec):

      # create a change tracker primed with the current change-spec
      tracker = pysyncml.AttributeChangeTracker(changeSpec)

      # create a temporary item that will hold the result of the merging
      tmpItem = MyItem()

      for attr, value in remoteItem.items():

        # this call will raise pysyncml.ConflictErrer on conflict
        tmpItem[attr] = tracker.update(attr, localItem[attr], value)

      # search for deleted fields
      for attr in localItem.keys():

        if attr in remoteItem:
          # this will have been checked in the first loop
          continue

        # this call will raise pysyncml.ConflictErrer on conflict
        tmpItem[attr] = tracker.update(attr, localItem[attr], None)

        if tmpItem[attr] is None:
          del tmpItem[attr]

      return self.replaceItem(tmpItem, True)

Note that this example used the :meth:`pysyncml.ChangeTracker.update
<pysyncml.change.tracker.ChangeTracker.update>` method, which
simplifies the value checking, but does result in potentially
redundant changes to the item. If more granular information is
required for optimization reasons, you can use the
:meth:`pysyncml.ChangeTracker.isChange
<pysyncml.change.tracker.ChangeTracker.isChange>` method. This,
however, requires that you check the values for equality before hand,
and treat the return value dependent on what kind of tracker is being
used.

Change-Spec Details
-------------------

As mentioned above, a "change-spec" is an opaque string which may be
concatenated with other change-specs and separated via a semicolon
(";"). Such a change-spec should be generated whenever a change is
made to the server-side of an item during a SyncML transaction. These
change-specs are intended to summarize and represent those changes and
attached to the change event, such that when another change is made,
it can be evaluated against the changes concurrently made by another
peer.

Changes are typically used to only track which "field" within an item
is changed so that merging of multiple changes to a single item can be
done. These changes typically include a checksum for the initial
value, not the actual changed value - this is used to minimize how
much storage is required to track changes. The reason that a checksum
of the initial value is needed is that the agent performing a merge
must be able to identify fields with competing changes and which ones
are actually a no-change change by comparing them to their initial
value. Note that the checksum is not needed for *added* fields, only
for modified and deleted fields.

For example, a contact agent may only record which fields of a contact
were modified along with the MD5
(e.g. "mod:lastname@d3b07384d113edec49eaa6238ad5ff00") and a file
agent may only record which lines of a file changed
(e.g. "mod:14@dd43af56ff406a8cf89fae4e1ac86722"). Note that in many
cases the MD5 of a changed field may actually be longer than the
actual value - it is up to the agent implementing the change-spec to
detect this and to potentially make some relevant optimizations (such
an optimization is already implemented by the `Change Tracking
Helpers`_).

Then, when resolving a conflict, the agent checks to see if the same
field was modified, and if not, a merge can happen. If the same field
was modified, then an automated merge is not possible, and the change
request falls back to being handled by the `conflictPolicy` (as
documented above).

When pysyncml is tracking changes (i.e. when running as the server
role), the agent will be called with `reportChanges` set to ``True``
in the call to :meth:`pysyncml.Agent.replaceItem
<pysyncml.agents.base.Agent.replaceItem>`. This indicates to the agent
that it should (if possible) return a change-spec that will later be
used when resolving conflicts. This change-spec should be a string (or
an object that supports coercion via ``str()``). If multiple changes
accumulate for the same item, they will be concatenated and separated
with a semicolon (";"). Semicolons used in the change-spec will *not*
be escaped -- it is the responsibility of the change-spec generator
to be aware of this. The reason is that this allows the change-spec
generator to create pre-aggregated change-specs.

During a merge attempt, pysyncml will call the agent's
:meth:`pysyncml.Agent.mergeItems
<pysyncml.agents.base.Agent.mergeItems>` method, with the current
local item, the new conflicting remote item and the accumulated
change-spec that is the source of the conflict. The agent must then
analyze the change-spec in the context of the local and remote item
states, and either refuse or perform the merge. If it cannot perform
the merge, it should raise a `pysyncml.ConflictError`, detailing which
field or fields caused the failure, such that the user can engage a
manual correction.

Example Merge
-------------

To illustrate the general workflow, let us assume that we are
implementing a contact agent, where each item is a contact that can
have fields such as "firstname", "lastname", "tel-mobile", "tel-home",
and "tel-pager".

At some point, the pysyncml server and two clients are completely
synchronized. Then, the first client modifies a particular record by
updating both the "lastname" and the "tel-pager" fields, and
synchronizes with the server. The server stores the new item and the
contact agent running on the server reports the following change-spec
for the item::

  mod:lastname@MD5,tel-pager@MD5

where the "MD5" is the MD5 checksum of the *initial* value before the
change was made. Then, before the second client synchronizes, the
first client modifies the record again, this time deleting the
"tel-pager" and adding a "tel-home" field. The client synchronizes
this change with the server, and the server contact agent reports the
following change-spec::

  del:tel-pager@MD5|add:tel-home

The server then notices that there is still a pending change on this
item for the second client, and concatenates the change-spec to::

  mod:lastname@MD5,tel-pager@MD5;del:tel-pager@MD5|add:tel-home

Now, the second client makes some changes to the contact and synchronizes
with the server. Now, the agent is provided with the above change-spec,
analyzes the changes requested by the second client, and either applies
them or cancels the operation.

For example, if the second client had modified "firstname" only, then
there is no conflict, and the agent can perform the merge. If,
however, there was a change to "lastname", then new value provided by
the remote client must be inspected. If the new value is not identical
to either the initial value stored on the change-spec (i.e. no change)
or the current value (i.e. it was changed the exact same way), then
the merge should raise a `pysyncml.ConflictError`.

.. ----------------------------------------------------------------------------
.. end of $Id: README.txt 24 2012-06-19 19:35:12Z griff1n $
.. ----------------------------------------------------------------------------
