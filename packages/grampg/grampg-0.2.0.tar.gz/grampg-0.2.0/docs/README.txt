The documentation in this tree is in plain text files, but it relies
heavily on the autodoc extension to Sphinx. The contents may not seem like
much, but the generated docs are quite thorough.

It uses ReST (reStructuredText) [1], and the Sphinx documentation system [2].
This allows it to be built into other forms for easier viewing and browsing.

To create an HTML version of the docs:

* Install Sphinx (using ``sudo pip install Sphinx`` or some other method)

* In this docs/ directory, type ``make html`` (or ``make.bat html`` on
  Windows) at a shell prompt.

The documentation in docs/_build/html/index.html can then be viewed in
a web browser.

[1] http://docutils.sourceforge.net/rst.html
[2] http://sphinx.pocoo.org/
