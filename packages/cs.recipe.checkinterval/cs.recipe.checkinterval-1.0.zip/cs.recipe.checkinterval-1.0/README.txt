Introduction
============

This products uses jarn.checkinterval product to calculate the 
value of the python-check-interval option in Zope's configuration.

It's integrated into zc.buildout process, so it's just a 3 line add
to your buildout, and each time you run it, you'll get the correct
value for your setup, so no more need to execute manually the script.

Configuration
==============

Add a part in your buildout file pointing to this recipe before
the part that creates the Zope instance, as follows::

  [buildout]
  parts = 
      ...
      checkinterval
      instance
      ...

  [checkinterval]
  recipe = cs.recipe.checkinterval

And then, just use the value provided by the recipe in your instance part::

  [instance]
  ...
  python-check-interval = ${checkinterval:value}
  ...

And that's it.

More about check-interval
===========================

Please, read `jarn.checkinterval`_'s README to get more information about it.


.. _`jarn.checkinterval`: http://pypi.python.org/pypi/jarn.checkinterval

