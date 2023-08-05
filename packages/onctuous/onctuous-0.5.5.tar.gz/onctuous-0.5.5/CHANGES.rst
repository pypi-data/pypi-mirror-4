==============
Onctuous 0.5.5
==============

This section documents all user visible changes included between Onctuous
versions 0.5.2 and Onctuous versions 0.5.5

Changes
-------

- Enhanced arror messages to be as descriptive as possible.
- Packaging fixes for Jenkins

==============
Onctuous 0.5.2
==============

This section documents all user visible changes included between Onctuous
versions 0.5.1 and Onctuous versions 0.5.2

Changes
-------

- packaging fixes
- ``Coerce`` is now idempotent

==============
Onctuous 0.5.1
==============

This section documents all user visible changes included between Onctuous
versions 0.5.0 and Onctuous versions 0.5.1

Includes niceties and bugfixes according to real-world(tm) libraries ddbmock and
dynamodb-mapper.

Additions
---------

- official, full documentation

Changes
-------

- split onctuous into sub-modules
- better error messages
- support for ``None`` as a default value

==============
Onctuous 0.5.0
==============

This section documents all user visible changes included between Voluptuous
versions 0.4.2 and Onctuous versions 0.5.0

Initial Voluptuous fork by Ludia. There was no changelog before.

Additions
---------

- ``default`` parameter to ``Required`` marker.
- 100% unit/functional tests
- lots comments

Changes
-------

- Renamed all validators to avoid built-in collisions
- InvalidList does not accept empty ``errors`` array
- lots of code cleanups

Removal
-------

- ``defaults_to``. It was inneficient and failed to add default value.
- most doctests
