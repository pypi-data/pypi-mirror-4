Introduction
============
``pyramid_recipe_modwgi`` is a `zc.buildout`_ recipe which create `mod_wsgi`_
entry point for your wsgi application.

Package was inspired by `collective.recipe.modwsgi`_.

.. contents::


Example
=======

    [buildout]
    parts = modwsgi

    [modwsgi]
    recipe = pyramid-recipe-modwsgi
    eggs = pyramid
    target = ${buildout:directory}/app.wsgi
    config-file = ${buildout:directory}/production.ini


Changelog
=========

0.1 - 05-10-2012
----------------

- Initial release
  [garbas]


Contributors
============

- `Rok Garbas`_


.. _`zc.buildout`: http://buildout.org
.. _`mod_wsgi`: http://code.google.com/p/modwsgi
.. _`collective.recipe.modwsgi`: https://github.com/wichert/collective.recipe.modwsgi
.. _`Rok Garbas`: http://garbas.si
.. _`garbas`: http://garbas.si
