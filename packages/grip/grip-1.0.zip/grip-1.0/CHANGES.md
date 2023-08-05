Grip Changelog
==============

Version 1.0 (2012-12-08)
------------------------

- CLI: now accepts an address, not just a port.
- CLI: now accepts --gfm and --context=<repo> arguments for rendering
  GitHub Flavored Markdown.
- API: `serve` function now accepts `None` for its arguments to
  indicate 'use default'.
- API: `serve` function now accepts a 'host'.
- API: `serve` now resolves the default file when given a path.
- Now using docopt for more advanced argument processing.
- Now using path-and-address for humanistic path / address handling.


Version 0.2.1 (2012-12-02)
--------------------------

- Issue #5: Fixed the installer to work in the case where
  the requirements are not already installed.


Version 0.2 (2012-12-01)
------------------------

- Github styles are now retrieved dynamically when run,
  instead of using the outdated styles from the config.


Version 0.1.1 (2012-11-20)
--------------------------

- Added the port command-line argument.


Version 0.1 (2012-11-19)
------------------------

First public preview release.
