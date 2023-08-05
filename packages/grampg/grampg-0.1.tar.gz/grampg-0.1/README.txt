
=======================================
grampg: Grumpy Admin Password Generator
=======================================

*Copyright 2012 Elvio Toccalino.*


ABOUT
=====

The **grampg** (cue to *Grumpy Admin Password Generator*, and pronounced "*grummpeegee*") is a small python2 library which allows to generate passwords according to (possibly complicated) *user specs*. The idea is simple: build an instance, feed it your desired specifications, then generate as many passwords as you want. Each password generated will be independent of the others, except from the fact that all of them will comply with the specs.

The objectives for the grampg are flexibility and easy of use. grampg fullfils by providing a *kind* interface to the user: When building the password generator the user writes the spec as if it were being pronounced. In this fashion, a set of complex rules is expressed in a declarative line.


USAGE
=====

Typical usage follows the pattern outlined before: build a generator instance, feed it your specs, collect your passwords. This brief explanation fails to explain *how*, which is the main attractive of the grampg. As an example, consider the following:

  Your admin needs your system to produce passwords of between 5 and 10 letters, at least 4 numbers, adding up to 10 characters total. Oh, and since this passwords may be used in some-mail-systeam, they should start with a letter.

The constrains, or *specs*, are quite contrived, but they can be fed to grampg simply::

  from grampg import PasswordGenerator
  passwords = (PasswordGenerator().of().between(5, 10, 'letters')
                                       .at_least(4, 'numbers')
                                       .length(10)
                                       .begining_with('letters')
                                       .done())
  return [passwords.generate() for i in xrange(so_many_passwords)]

Only one generator instance is created, and then used to produce as many passwords as are required.

Other character sets available by default are 'lower_letters', 'upper_letters', and 'alphanumeric', but the user is free to build generator instances with any character sets desired (as well as overriding the defaults). For example::

  passwords = (PasswordGenerator({'special': list('%$#!*'), 'letters': list('abcde')})
                                .of().exactly(3, special).at_most(2, 'special').done())

For usage more examples, excecute and read the **many_passwords.py** program (which lives in ``grampg/demo``), a simple program that spits passwords according to somewhat realistic specifications. There is also the usecases.py file, which consists of many uses of the grampg and their expected output (both valid and not).


TESTS
=====

The grampg package includes two files which purpose is to serve as test bed:

**tests.py**
  Unit test suite.

**usecases.py**
  Integration tests.

**regression.py**
  Regression tests. Like integrations, but actual examples that went awry and are now fixed.


ABOUT THE NAME
==============

The name sucks, I know. It's meant as a silly joke to the person who inspired the code creation.


LICENCE
=======

The ``grampg`` software package (including tests, documentation and demonstration programs) is licensed under the GNU Affero GPL version 3.0. A copy of the license is included with the grampg package. For details about the license, visit http://www.gnu.org/licenses/agpl.html.
