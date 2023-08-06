History of collective.recipe.i18noverrides
==========================================

1.2 (2013-01-23)
----------------

- Raise ``zc.buildout.UserWarning`` in case of errors.  This is how it
  should be done.  It is more noticeable than logging an error (which
  may not be really visible as error) and quitting.
  [maurits]


1.1 (2012-09-13)
----------------

- Moved to github:
  https://github.com/collective/collective.recipe.i18noverrides
  [maurits]


1.0 (2010-08-25)
----------------

- Added a note to warn that this recipe will have no effect in Plone 4
  (Zope 2.12) or higher.  You should create an own package and
  register a locales directory there.
  [maurits]


0.4 (2009-09-08)
----------------

- Only consider buildout parts for inclusion in the destinations when
  they are actually in the parts section of buildout.  Otherwise you
  can run into errors like this:
  Error: Missing option: zptdebugger:__buildout_signature__
  [maurits]


0.3 (2009-09-08)
----------------

- If no destinations are specified, we automatically copy the po files
  to all parts that use plone.recipe.zope2instance.
  [maurits]


0.2 (2009-08-12)
----------------

- Allow to specify an egg (with optional package)
  where the source directory can be found.
  [gotcha]

- Pin packages (at least zc.buildout) in both the main buildout.cfg
  and the one in the tests, to avoid test failures simply because the
  used zc.buildout is upgraded during the test run.
  [maurits]


0.1 (2009-06-05)
----------------

- Initial implementation moved over from a one-off script.  [maurits]

- Created recipe with ZopeSkel
  [Maurits van Rees]
