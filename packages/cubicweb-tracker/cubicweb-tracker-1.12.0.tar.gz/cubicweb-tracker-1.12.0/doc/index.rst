The Tracker security model
==========================

Cubicweb-tracker comes with a predefined security model and a test
suit for it.

Cubicweb security
-----------------

The basic model of CubicWeb is based on permissions defined on the
data model.

There are two kinds of data : entities and relations. Entities
operations are create, read, update, delete. Relation operations are
create, read, delete. Each of these operations can be assigned to a
fixed set of user groups (aka access control list) on a per-entity and
per-relation basis.

Default groups:

* managers
* users
* guests
* owners

CubicWeb provides an entity called CWPermission which allows to write
more sophisticated security models. Tracker uses this to provide a
per-project access control list.

Tracker security
----------------

Tracker adds the `staff` group to represent users having a privileged
access to projects. For more fine-grained control, Tracker provides
the following project-local roles:

* developer
* client

The `more actions` -> `permission settings` gives administrator read
access to the global permission settings and also allows to manage
user groups to project-local permissions mappings.

A small example
---------------

Project leader of Tartempion Inc. builds an extranet for him and his
client to comunicate over the state of an important piece of
software. His crew is set in a `tartempion` group but only a fraction
of them should be developers on this project. Same for the client
side: they are all in the `whizbang_retail` group but only two of them
should interact with the tracker.

Hence when he creates the `Whizbang online` project he sets up two new
groups, `whiz_dev` and `whiz_cli`, and creates two new permissions
`developer (whiz)` and `client (whiz)` which establish a mapping from
the developer permission (resp. client) to whiz_dev (resp. whiz_cli)
groups.

Operations matrix
-----------------

+----------------------------------+-----+------+---------+---------+
|operation / group                 |user |client|developer|staff    |
+----------------------------------+-----+------+---------+---------+
|create project                    |     |      |         |X        |
+----------------------------------+-----+------+---------+---------+
|udpate project                    |     |      |         |X (owner)|
+----------------------------------+-----+------+---------+---------+
|create ticket                     |     |X     |X        |X        |
+----------------------------------+-----+------+---------+---------+
|udpate ticket                     |     |      |X        |X        |
+----------------------------------+-----+------+---------+---------+
|start dev. on ticket              |     |      |X        |X        |
+----------------------------------+-----+------+---------+---------+
|modify ticket in progress         |     |      |X        |X        |
+----------------------------------+-----+------+---------+---------+
|close ticket                      |     |X     |X        |X        |
+----------------------------------+-----+------+---------+---------+
|create version                    |     |X     |X        |X        |
+----------------------------------+-----+------+---------+---------+
|affect ticket in planned version  |     |X     |X        |X        |
+----------------------------------+-----+------+---------+---------+
|change ticket version             |     |      |X        |X        |
+----------------------------------+-----+------+---------+---------+
|remove ticket from planned version|     |X     |X        |X        |
+----------------------------------+-----+------+---------+---------+
|start development of version      |     |      |X        |X        |
+----------------------------------+-----+------+---------+---------+

