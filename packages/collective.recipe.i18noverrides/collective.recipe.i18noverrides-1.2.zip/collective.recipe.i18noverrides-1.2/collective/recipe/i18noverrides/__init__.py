# -*- coding: utf-8 -*-
"""Recipe i18noverrides"""

import logging
import os
import shutil
import pkg_resources
import zc.buildout

logger = logging.getLogger('collective.recipe.i18noverrides')


class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

    def configure(self):
        source = self.options.get('source')
        egg_spec = self.options.get('egg', None)
        if egg_spec is not None:
            source = self.sourceFromEgg(egg_spec, source)

        destinations = self.options.get('destinations', '')
        destinations = [d for d in destinations.splitlines() if d]
        if not destinations:
            parts = self.buildout['buildout']['parts']
            part_names = parts.split()
            destinations = []
            for part_name in part_names:
                part = self.buildout[part_name]
                if part.get('recipe') == 'plone.recipe.zope2instance':
                    destinations.append(part['location'])
        for dir in [source] + destinations:
            if not os.path.exists(dir):
                raise zc.buildout.UserError(
                    "path %r does not exist. You must list the %s part "
                    "after all plone.recipe.zope2instance parts." % (
                        dir, self.name))
            if not os.path.isdir(dir):
                error = 'path %r must be a directory.' % dir
                raise zc.buildout.UserError(error)
        self.destinations = destinations
        self.source = source

    def sourceFromEgg(self, egg_spec, source):
        if os.path.abspath(source) == source:
            error = ("Because egg option is provided,\n"
                     "source '%s' should be relative, not absolute." % source)
            raise zc.buildout.UserError(error)
        package_name = self.options.get('package', egg_spec)
        try:
            req = pkg_resources.Requirement.parse(egg_spec)

            buildout = self.buildout
            buildout_options = buildout['buildout']
            if pkg_resources.working_set.find(req) is None:
                if buildout.offline:
                    dest = None
                    path = [buildout_options['develop-eggs-directory'],
                            buildout_options['eggs-directory'],
                            ]
                else:
                    dest = buildout_options['eggs-directory']
                    path = [buildout_options['develop-eggs-directory']]

                zc.buildout.easy_install.install(
                    [egg_spec], dest,
                    links=buildout._links,
                    index=buildout_options.get('index'),
                    path=path,
                    working_set=pkg_resources.working_set,
                    newest=buildout.newest,
                    allow_hosts=buildout._allow_hosts)
            package = __import__(package_name, {}, {}, '__doc__')
        except ImportError:
            error = 'Package %r could not be imported.' % package_name
            raise zc.buildout.UserError(error)
        path = os.path.dirname(package.__file__)
        return os.path.join(path, source)

    def install(self):
        """Installer"""
        self.configure()
        po_files = [f for f in os.listdir(self.source) if f.endswith('.po')]
        if len(po_files) == 0:
            # Note that logger.warn does not print 'Warning'
            # automatically for some reason, so we add it manually.
            logger.warn('Warning: source %r contains no .po files.',
                        self.source)
            return tuple()

        created = []
        if not self.destinations:
            logger.warn('No destinations specified.')
            return tuple()

        for destination in self.destinations:
            i18n_dir = os.path.join(destination, 'i18n')
            if not os.path.exists(i18n_dir):
                logger.info("Creating directory %s" % i18n_dir)
                os.mkdir(i18n_dir)
                created.append(i18n_dir)
            if not os.path.isdir(i18n_dir):
                error = "%r is not a directory." % i18n_dir
                raise zc.buildout.UserError(error)
            for po_file in po_files:
                file_path = os.path.join(self.source, po_file)
                shutil.copy(file_path, i18n_dir)
                created.append(os.path.join(i18n_dir, po_file))

        logger.info('Copied %d po files.' % len(po_files))

        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.

        # XXX Returning 'created' here gives test errors now.  We will
        # have to see if this is really needed in our use case, as the
        # zope instances likely get removed anyway.  But if a source
        # file was removed meanwhile, we will have to remove it in the
        # destinations as well.  But zc.buildout should do this
        # automatically and even when returning 'created' I do not see
        # that happening.  So we will ignore it.
        return tuple()

    # It is easiest if the updater does the same as the installer.
    update = install
