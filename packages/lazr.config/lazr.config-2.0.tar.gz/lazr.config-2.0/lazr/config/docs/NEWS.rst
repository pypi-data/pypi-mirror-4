====================
NEWS for lazr.config
====================


2.0 (2013-01-10)
================
- Ported to Python 3.
- Now more strict in its requirement of ASCII in config files.
- Category names are now sorted by default.


1.1.3 (2009-08-25)
==================

- Fixed a build problem.

1.1.2 (2009-08-25)
==================

- Got rid of a sys.path hack.


1.1.1 (2009-03-24)
==================

- License clarification: only v3 of the LGPL is offered at this time, not
  subsequent versions.

- Build is updated to support Sphinx docs and other small changes.

1.1 (2009-01-05)
================

- Support for adding arbitrary sections in a configuration file, based on a
  .master section in the schema.  The .master section allows admins to define
  configurations for an arbitrary number of processes.  If the schema defines
  .master sections, then the conf file can contain sections that extend the
  .master section.  These are like categories with templates except that the
  section names extending .master need not be named in the schema file.
  [Bug 310619]

- ConfigSchema now provides an interface for constructing the schema from a
  string.  [Bug 309859]

- Added as_boolean() and as_log_level() type converters.  [Bug 310782]

- getByCategory() accepts a default argument.  If the category is missing, the
  default argument is returned.  If the category is missing and no default
  argument is given, a NoCategoryError is raised, as before.  [Bug 309988]


1.0 (2008-12-19)
================

- Initial release
