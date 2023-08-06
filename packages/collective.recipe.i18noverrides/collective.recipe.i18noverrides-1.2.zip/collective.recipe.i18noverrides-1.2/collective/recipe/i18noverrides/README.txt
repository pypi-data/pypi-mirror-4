Supported options
=================

The recipe supports the following options:

source
    Source directory that contains the .po files that the recipe will
    copy.  All ``*.po`` files will be copied.  This option is mandatory.

egg
    Egg that contains the ``source`` directory. If this option is mentioned,
    the ``source`` directory has to be a relative path.

package
    Can be mentioned when ``source`` cannot be found in ``egg`` for one of the
    following reasons : ``egg`` holds a version specification; ``egg`` is not
    equal to the name of the installed package; ``source`` is in a subpackage.

destinations
    Target directory or directories.  This should point to the
    directory of the zope 2 instance.  The recipe will create an i18n
    directory in each of the destinations and copy all ``*.po`` files
    from the source directory to these i18n directories.  This option
    is mandatory.


Example usage
-------------

We'll start by creating a buildout that uses the recipe.  Here is a
template where we only have to fill in the source and destinations::

    >>> buildout_config_template = """
    ... [buildout]
    ... index = http://pypi.python.org/simple
    ... parts = i18noverrides
    ... versions = versions
    ...
    ... [versions]
    ... zc.buildout = 1.4.3
    ... zc.recipe.egg = 1.2.2
    ... setuptools = 0.6c11
    ... distribute = 0.6.14
    ...
    ... [i18noverrides]
    ... recipe = collective.recipe.i18noverrides
    ... source = %(source)s
    ... destinations = %(dest)s
    ... """

We will start with specifying some non existing source and destination
directories::

    >>> write('buildout.cfg', buildout_config_template % {
    ... 'source': '${buildout:directory}/translations',
    ... 'dest': '${buildout:directory}/instance'})

Running the buildout gives us::

    >>> print system(buildout)
    Installing i18noverrides.
    While:
      Installing i18noverrides.
    Error: path '/sample-buildout/translations' does not exist. You must list the i18noverrides part after all plone.recipe.zope2instance parts.
    <BLANKLINE>

The source must be a directory::

    >>> write('translations', 'This is a file.')
    >>> print system(buildout)
    Installing i18noverrides.
    While:
      Installing i18noverrides.
    Error: path '/sample-buildout/translations' must be a directory.
    <BLANKLINE>

Now we remove this file and try with a proper directory::

    >>> remove('translations')
    >>> mkdir('translations')
    >>> print system(buildout)
    Installing i18noverrides.
    While:
      Installing i18noverrides.
    Error: path '/sample-buildout/instance' does not exist. You must list the i18noverrides part after all plone.recipe.zope2instance parts.
    <BLANKLINE>

So we set a destination too and first try with a file as well before
creating a directory::

    >>> write('instance', 'This is a file.')
    >>> print system(buildout)
    Installing i18noverrides.
    While:
      Installing i18noverrides.
    Error: path '/sample-buildout/instance' must be a directory.
    <BLANKLINE>
    >>> remove('instance')
    >>> mkdir('instance')
    >>> print system(buildout)
    Installing i18noverrides.
    collective.recipe.i18noverrides: Warning: source '/sample-buildout/translations' contains no .po files.
    <BLANKLINE>

Now the source and destination have been setup correctly, but we get a
warning as the source directory has no translation files.  We first
add a file that does not end with ``.po``.  Since the previous
buildout run only had a warning and finished successfully, the recipe
now runs in update mode, which does the same as the install mode::

    >>> write('translations', 'not-a-po-file', 'I am not a po file')
    >>> print system(buildout)
    Updating i18noverrides.
    collective.recipe.i18noverrides: Warning: source '/sample-buildout/translations' contains no .po files.
    <BLANKLINE>
    >>> write('translations', 'plone-nl.po', 'I am a Dutch plone po file')
    >>> write('translations', 'plone-de.po', 'I am a German plone po file')
    >>> print system(buildout)
    Updating i18noverrides.
    collective.recipe.i18noverrides: Creating directory /sample-buildout/instance/i18n
    collective.recipe.i18noverrides: Copied 2 po files.
    <BLANKLINE>

No warnings, no errors, so let's see what the end result is::

    >>> ls('translations')
    -  not-a-po-file
    -  plone-de.po
    -  plone-nl.po
    >>> ls('instance')
    d  i18n

A i18n directory has been created in the instance.  Inside that
directory we find our two po files::

    >>> ls('instance', 'i18n')
    -  plone-de.po
    -  plone-nl.po
    >>> cat('instance', 'i18n', 'plone-de.po')
    I am a German plone po file
    >>> cat('instance', 'i18n', 'plone-nl.po')
    I am a Dutch plone po file

If the destination directory for some strange reason already contains
a i18n file instead of a directory, we fail::

    >>> remove('instance', 'i18n')
    >>> write('instance', 'i18n', 'I am a file')
    >>> print system(buildout)
    Updating i18noverrides.
    While:
      Updating i18noverrides.
    Error: '/sample-buildout/instance/i18n' is not a directory.
    <BLANKLINE>
    >>> remove('instance', 'i18n')

It should also be possible to have multiple destinations::

    >>> write('buildout.cfg', buildout_config_template % {
    ... 'source': '${buildout:directory}/translations',
    ... 'dest': """
    ...     ${buildout:directory}/instance
    ...     ${buildout:directory}/instance2"""})
    >>> print system(buildout)
    Installing i18noverrides.
    While:
      Installing i18noverrides.
    Error: path '/sample-buildout/instance2' does not exist. You must list the i18noverrides part after all plone.recipe.zope2instance parts.
    <BLANKLINE>

Right, right, we will create that directory too::

    >>> mkdir('instance2')
    >>> print system(buildout)
    Installing i18noverrides.
    collective.recipe.i18noverrides: Creating directory /sample-buildout/instance/i18n
    collective.recipe.i18noverrides: Creating directory /sample-buildout/instance2/i18n
    collective.recipe.i18noverrides: Copied 2 po files.
    <BLANKLINE>

Let's check the result::

    >>> ls('instance')
    d  i18n
    >>> ls('instance', 'i18n')
    -  plone-de.po
    -  plone-nl.po
    >>> ls('instance2')
    d  i18n
    >>> ls('instance2', 'i18n')
    -  plone-de.po
    -  plone-nl.po
    >>> cat('instance2', 'i18n', 'plone-de.po')
    I am a German plone po file
    >>> cat('instance2', 'i18n', 'plone-nl.po')
    I am a Dutch plone po file

Clean up:

    >>> remove('instance')
    >>> remove('instance2')


Integration with plone.recipe.zope2instance
-------------------------------------------

As the recipe is normally used to add translations to zope 2
instances, it makes sense to search for buildout parts that setup zope
instances and take those locations.

    >>> write('buildout.cfg', """
    ... [buildout]
    ... index = http://pypi.python.org/simple
    ... parts = instance instance2 zeoclient i18noverrides
    ... versions = versions
    ...
    ... [versions]
    ... zc.buildout = 1.4.3
    ... zc.recipe.egg = 1.2.2
    ... setuptools = 0.6c11
    ... distribute = 0.6.14
    ... plone.recipe.zope2instance = 3.9
    ... mailinglogger = 3.3
    ...
    ... [i18noverrides]
    ... recipe = collective.recipe.i18noverrides
    ... source = ${buildout:directory}/translations
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... user = admin:admin
    ...
    ... [instance2]
    ... recipe = plone.recipe.zope2instance
    ... user = admin:admin
    ...
    ... [zeoclient]
    ... recipe = plone.recipe.zope2instance
    ... user = admin:admin
    ... """)

We mock a mkzopeinstance script in the bin directory:

    >>> write('bin/mkzopeinstance', """
    ... import sys
    ... import os
    ... path = sys.argv[2]
    ... os.mkdir(path)
    ... os.mkdir(os.path.join(path, 'etc'))
    ... """)

We do not want to install a complete zope2 instance in the tests, so
we do not add it to the buildout parts.  That does mean that running
buildout now fails:

    >>> print system(buildout)
    Getting distribution for 'plone.recipe.zope2instance==3.9'.
    ...
    Installing instance.
    Generated script '.../bin/instance'.
    ...
    Installing i18noverrides.
    collective.recipe.i18noverrides: Creating directory .../i18n
    collective.recipe.i18noverrides: Creating directory .../i18n
    collective.recipe.i18noverrides: Creating directory .../i18n
    collective.recipe.i18noverrides: Copied 2 po files.
    <BLANKLINE>
    >>> ls('parts', 'instance')
    d etc
    d i18n
    >>> ls('parts', 'instance', 'i18n')
    -  plone-de.po
    -  plone-nl.po
    >>> ls('parts', 'instance2', 'i18n')
    -  plone-de.po
    -  plone-nl.po
    >>> ls('parts', 'zeoclient', 'i18n')
    -  plone-de.po
    -  plone-nl.po

If we explicitly specify destinations, the recipes are ignored.

    >>> write('buildout.cfg', """
    ... [buildout]
    ... index = http://pypi.python.org/simple
    ... parts = dummy i18noverrides
    ... versions = versions
    ...
    ... [versions]
    ... zc.buildout = 1.4.3
    ... zc.recipe.egg = 1.2.2
    ... setuptools = 0.6c11
    ... distribute = 0.6.14
    ... plone.recipe.zope2instance = 3.9
    ... mailinglogger = 3.3
    ...
    ... [i18noverrides]
    ... recipe = collective.recipe.i18noverrides
    ... source = ${buildout:directory}/translations
    ... destinations = ${buildout:directory}/dest
    ...
    ... [dummy]
    ... recipe = plone.recipe.zope2instance
    ... user = admin:admin
    ... """)
    >>> mkdir('dest')
    >>> print system(buildout)
    Uninstalling ...
    Installing i18noverrides.
    collective.recipe.i18noverrides: Creating directory /.../dest/i18n
    collective.recipe.i18noverrides: Copied 2 po files.
    <BLANKLINE>
    >>> ls('parts', 'dummy')
    d etc
    >>> ls('dest', 'i18n')
    -  plone-de.po
    -  plone-nl.po

Clean up:

    >>> remove('translations')


Usage with directory in egg
---------------------------

We start by creating a buildout that uses the recipe.  Here is a
template where we only have to fill in the source, egg and
destinations::

    >>> buildout_config_template = """
    ... [buildout]
    ... index = http://pypi.python.org/simple
    ... parts = i18noverrides
    ... versions = versions
    ...
    ... [versions]
    ... zc.buildout = 1.4.3
    ... zc.recipe.egg = 1.2.2
    ... setuptools = 0.6c11
    ... distribute = 0.6.14
    ... # We need to pin this one because it still needs to be uninstalled.
    ... # If we do not pin, the uninstall code will get the latest version,
    ... # which depends on Zope2, which means we are hosed...
    ... plone.recipe.zope2instance = 3.9
    ... mailinglogger = 3.3
    ...
    ... [i18noverrides]
    ... recipe = collective.recipe.i18noverrides
    ... source = %(source)s
    ... egg = %(egg)s
    ... destinations = %(dest)s
    ... """

We specify ``egg`` and ``source``::

    >>> write('buildout.cfg', buildout_config_template % {
    ... 'source': 'tests/translations',
    ... 'egg': 'collective.recipe.i18noverrides',
    ... 'dest': 'translations'})

We prepare target directory::

    >>> mkdir('translations')

Running the buildout gives us::

    >>> print system(buildout)
    Uninstalling ...
    Installing i18noverrides.
    collective.recipe.i18noverrides: Creating directory translations/i18n
    collective.recipe.i18noverrides: Copied 2 po files.
    <BLANKLINE>

Let's check the result::

    >>> ls('translations')
    d  i18n
    >>> ls('translations', 'i18n')
    -  test-fr.po
    -  test-nl.po
    >>> cat('translations', 'i18n', 'test-fr.po')
    Un fichier .po
    >>> cat('translations', 'i18n', 'test-nl.po')
    Een .po bestand

We specify ``egg`` and an absolute path in ``source``::

    >>> write('buildout.cfg', buildout_config_template % {
    ... 'source': '/translations',
    ... 'egg': 'testegg',
    ... 'dest': 'translations'})

Running the buildout gives us::

    >>> print system(buildout)
    Uninstalling i18noverrides.
    Installing i18noverrides.
    While:
      Installing i18noverrides.
    Error: Because egg option is provided,
    source '/translations' should be relative, not absolute.
    <BLANKLINE>

We specify an `egg`` that does not hold the configured ``source``::

    >>> write('buildout.cfg', buildout_config_template % {
    ... 'source': 'translations',
    ... 'egg': 'zc.recipe.egg',
    ... 'dest': 'translations'})

Running the buildout gives us::

    >>> print system(buildout)
    Installing i18noverrides.
    While:
      Installing i18noverrides.
    Error: path '/sample-buildout/eggs/zc.recipe.egg.../zc/recipe/egg/translations' does not exist. You must list the i18noverrides part after all plone.recipe.zope2instance parts.
    <BLANKLINE>
