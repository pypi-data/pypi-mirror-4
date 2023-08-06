Changelog
=========

0.2.0 (2013-05-03)
------------------

New
~~~

- Support for iteration in sequence and struct in one go. [Valentin Lab]

- Generate the ``setup.py`` files from ``setup.cfg`` so that PyPI
  packages are compatible with ``setuptools``-like installers (as
  ``pip``). [Valentin Lab]

Fix
~~~

- Doc: forgot to mention ``./autogen.sh`` execution when getting the
  code from git, and be more clear about other means of installation.
  [Valentin Lab]

- Generated ``setup.py`` do not support file names on the same line,
  this prevented installation via ``pip install``. [Valentin Lab]

0.1.3 (2013-03-29)
------------------

Fix
~~~

- Removed the spurious line feed at the end of any ``shyaml`` output.
  [Valentin Lab]

- Support querying for... nothing. Which now returns the whole input
  YAML. [Valentin Lab]

  Before this fix, you couldn't ask for ``shyaml get-value`` alone, even
  if it makes sense but is completely useless as it returns the whole
  YAML input.

0.1.2 (2013-03-23)
------------------

New
~~~

- Support for list indexes (see README.rst). [Valentin Lab]

- Catch exceptions when parsing structure and output a clean error
  message. [Valentin Lab]

0.1.1 (2013-02-27)
------------------

Changes
~~~~~~~

- Doc: some minor enhancements, and an "Install" section. [Valentin Lab]


