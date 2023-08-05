
``buildout.packagename`` is a `zc.buildout`_ extension which can be used
to extract the package name of an adjacent ``setup.py`` to avoid redundancy.
The extracted name is made available via the ``package-name`` variable in
the ``[buildout]`` section, i.e. as ``${buildout:package-name}``.

.. _`zc.buildout`: http://pypi.python.org/pypi/zc.buildout

Usage
-----

An example ``buildout.cfg`` using the extension might look like this::

  [buildout]
  extensions = buildout.packagename
  parts = app
  
  [app]
  recipe = zc.recipe.egg
  interpreter = app
  eggs = ${buildout:package-name}

Please note that since using this extension only makes sense for
package-specific buildouts, the `develop` setting is set to "."
for added convenience.
