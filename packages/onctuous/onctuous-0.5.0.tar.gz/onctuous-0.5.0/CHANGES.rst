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
