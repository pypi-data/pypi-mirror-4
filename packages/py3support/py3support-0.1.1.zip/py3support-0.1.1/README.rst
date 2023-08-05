Py3support
==========

Check which of your dependencies already support python 3.

Usage
-----

Example::

   $ py3support requirements.txt

   Python 3 support level: 50% (2/4)

   Python 3
   ========
     requests==1.0.4  
     docutils==0.10  

   Python 2
   ========
     Flask==0.9

   Unknown
   =======
     PIL==1.1.6


How it works
------------
The only easy way to tell if package supports python 3 is to trust `author's classifiers`_.
This tool hits PyPI index to check what python versions do your dependencies support.

Caveats
~~~~~~~
Some packages might support python 3, but do not have required metadata,
some packages might state py3 support, but it's not there yet (gunicorn). After all, a lot
of package authors don't provide python version classifiers at all.

.. _author's classifiers: http://docs.python.org/3/howto/pyporting.html#universal-bits-of-advice

Todo
----

* If not requirements.txt exists make use of pip freeze
* Check python 3 compatibility for latest version in PyPI
* Handle development versions -e
* Search for python 3 forks at github
* Handle package names with wrong CaSe (?)