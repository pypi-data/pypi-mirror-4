=======================
Advanced zeopack recipe
=======================

The built-in zeopack component of the various plone server recipes is great,
but we've got a couple of gaps:

 * Before we started using zeopack we are a custom packer that would rotate the
   backups made, allowing us to keep a few days of backups of our Data.fs.  We
   missed it.

 * There isn't a zeopack-all to pack all your storages.

 * You can't control pack-days from the command line so you can't have
   different packing preferences per storage.

This recipe can pack all storages configured using your ``zeoserver`` and
``filestorage`` recipes.


The recipe
==========

This recipe is meant to co-operate with the following zeoserver recipes:

 * https://github.com/plone/plone.recipe.zeoserver
 * http://pypi.python.org/pypi/plone.recipe.zope2zeoserver
 * https://github.com/isotoma/isotoma.recipe.zeo

It will use the zeopack settings set in these recipes (for example, pack credentials and ``pack-days``).

It will also configure itself to pack any storages specified through the following recipes::

 * http://pypi.python.org/pypi/collective.recipe.filestorage
 * https://github.com/isotoma/isotoma.recipe.zope2instance/ (isotoma.recipe.zope2instance:filestorage)

An example of its use would be something like this::

    [zeo]
    recipe = isotoma.recipe.zeo
    pack-rotate-days = 7

    [filestorage_portal_catalog]
    location = var/filestorage/catalog.fs
    zodb-mountpoint = /portal/portal_catalog
    zodb-cache-size = 100000
    zeo-client-cache-size = 512MB
    pack-rotate-days = 0
    pack-days = 0

    [filestorage]
    recipe = isotoma.recipe.zope2instance:filestorage
    zeo = zeo
    parts = portal_catalog

    [zeopack]
    recipe = isotoma.recipe.zeopack
    zeoserver = zeo
    filestorage = filestorage


The script
==========

If you use the recipe with a part called ``zeopack`` (as above) then you will
have a ``bin/zeopack``. If this is invoked with no arguments it will run with
little output on stdout - only high severity events will be output.

Running ``bin/zeopack`` with ``-v`` will but it into verbose mode. Adding a 2nd
``-v`` will make it even more verbose.

You can use ``-d`` to turn on more debug output. Right now this just means you
see log output from the zeo code as well as the zeopack code.

