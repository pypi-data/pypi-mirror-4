.. contents::

Introduction
============

tox require a virtualenv installed to run correctly. Since I sort of hate virtualenv I've created this recipe to run tox with buildout.

Usage
=====

Add this to your buildout::

    [tox]
    recipe = gp.recipe.tox

This will install a virtualenv with tox installed in `parts/tox/`

It's recommended to add this to your `~/.buildout/default.cfg`::

    [buildout]
    tox-install-dir = /home/gawel/.buildout/tox

This will install tox's virtualenv once for all your buildouts. You'll get a
`bin/tox binary` to run tests
