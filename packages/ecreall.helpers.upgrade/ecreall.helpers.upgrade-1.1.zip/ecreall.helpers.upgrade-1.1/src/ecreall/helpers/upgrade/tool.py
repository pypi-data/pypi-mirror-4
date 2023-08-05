from copy import copy
import logging

from ZODB.POSException import ConflictError
from zope.interface import implements
from zope.component import adapts

from Products.GenericSetup.upgrade import _upgrade_registry
from Products.GenericSetup.interfaces import ISetupTool
from Products.CMFCore.utils import getToolByName

LOG = logging.getLogger('Upgrade Tool')

from interfaces import IUpgradeTool
import transaction

class UpgradeTool(object):

    implements(IUpgradeTool)
    adapts(ISetupTool)

    def __init__(self, context):
        self.psetup = context
        self.portal = context.aq_inner.aq_parent
        self.qitool = self.portal.portal_quickinstaller

    def refreshResources(self):
        """Refresh all resource registries
        """
        css_tool = getToolByName(self.portal, 'portal_css')
        css_tool.cookResources()

        js_tool = getToolByName(self.portal, 'portal_javascripts')
        js_tool.cookResources()

        kss_tool = getToolByName(self.portal, 'portal_kss')
        kss_tool.cookResources()

        return "Js, kss and css refreshed"

    def runUpgradeSteps(self, steps):
        """Run upgrade step of a profile towards a destination
        @param steps is a tuple of (profile, destination)
        """
        for profile, destination in steps:
            self.runUpgradeStep(profile, destination)

    def runUpgradeStep(self, profile, destination):
        """Run upgrade step of a profile towards a destination
        """
        if not ':' in profile:
            profile = '%s:default' % profile

        upgrades = self.psetup.listUpgrades(profile, show_old=True)
        destpath = tuple(destination.split('.'))
        for upgrade in upgrades:
            if isinstance(upgrade, list):
                steps = [u['id'] for u in upgrade if u['dest'] == destpath]
                if steps:
                    steps_to_run = steps
                    break
            else:
                if upgrade['dest'] == destpath:
                    steps_to_run = [upgrade['id']]
                    break
        if not steps_to_run:
            raise KeyError, "Upgrade %s doesn't exist in profile %s" % (destination, profile)

        for step_id in steps_to_run:
            upgrade_step = _upgrade_registry.getUpgradeStep(profile, step_id)
            upgrade_step.doStep(self.psetup)

        # update profile upgrade version
        self.psetup._profile_upgrade_versions[profile] = destpath
        LOG.info("Ran %s upgrade step %s", profile, destination)

    def installProduct(self, product):
        self.qitool.installProduct(product)
        LOG.info("Installed %s", product)

    def uninstallProduct(self, product):
        self.qitool.uninstallProducts([product])
        LOG.info("Uninstalled %s", product)

    def reinstallProduct(self, product):
        self.qitool.installProduct(product)
        LOG.info("Reinstalled %s", product)

    def runProfile(self, profile, purge_old=False):
        if not ':' in profile:
            profile = '%s:default' % profile

        self.psetup.runAllImportStepsFromProfile('profile-%s' % profile, purge_old=purge_old)


    def runImportStep(self, profile, importstep, purge_old=False):
        if not ':' in profile:
            profile = 'profile-%s:default' % profile
        else:
            profile = 'profile-%s' % profile
        self.psetup.runImportStepFromProfile(profile,
                                             importstep, run_dependencies=False,
                                             purge_old=purge_old)

    def updateIndexes(self, index_tuples, catalogs=['portal_catalog'], reindex=True):
        """
        add and/or reindex indexes of catalogs

        @param index_tuples list of tuples [(index, index_type)]

        BE CAREFUL, IT ADD INDEXES IF NOT EXISTS
        """
        portal = self.portal
        if type(catalogs) not in (tuple, list):
            catalogs = [catalogs]
        catalogs = [getToolByName(portal, c) for c in catalogs]
        msgs = []
        for catalog in catalogs:
            for index, index_type in index_tuples:
                if not index in catalog.indexes():
                    catalog.addIndex(index, index_type)
                    msg = "Added %s index in %s catalog" % (index, catalog.id)
                    LOG.info(msg)
                    msgs.append(msg)
                if reindex:
                    LOG.info("reindex index %s on catalog %s", index, catalog.id)
                    catalog.reindexIndex(index, portal.REQUEST)
                transaction.savepoint(optimistic=True)
            LOG.info("Updated %s catalog", catalog.id)
        indexes_msg = ", ".join([i for i, t in index_tuples])
        transaction.savepoint(optimistic=True)
        msgs.append("Updated %s indexes" % indexes_msg)
        return msgs

    def migrateContent(self, portal_types, method,
                       catalogs=('portal_catalog',), query=None,
                       nofail=True, commit=False, stop_at_count=0):
        """ apply method on portal_types contents of catalogs """

        portal = self.portal

        if type(portal_types) not in (tuple, list):
            portal_types = [portal_types]

        brains = []
        if query:
            query = copy(query)
        else:
            query = {}

        query.update({'portal_type': portal_types})

        for catalog in catalogs:
            catalog = getToolByName(portal, catalog)
            brains += catalog.unrestrictedSearchResults(query)

        LOG.info("Migrate %s contents with %s method", ", ".join(portal_types), method.__name__)
        LOG.info("%s objects to migrate", len(brains))
        count = 0
        successes = 0
        failures = 0
        from webdav.EtagSupport import EtagSupport
        EtagSupport._http__refreshEtag = EtagSupport.http__refreshEtag
        # avoid to modify the object
        # 5 ko is an approximate size of an Archetypes object on the filesystem
        EtagSupport.http__refreshEtag = lambda x: ""
        for count, brain in enumerate(brains):
            if stop_at_count and count == stop_at_count:
                break

            try:
                path = brain.getPath()
                LOG.debug(path)
            except KeyError, e:
                LOG.warning("Catalog entry %s is corrupted : %s", str(brain), str(e))
                continue
            try:
                obj = brain.getObject()
            except AttributeError:
                LOG.warning("Invalid catalog entry at %s", path)
                continue

            try:
                method(obj, path=brain.getPath())
                if not obj._p_changed:
                    LOG.debug("Deactivate object %s", obj.getId())
                    obj._p_deactivate()
                else:
                    LOG.debug('Object has changes')
                successes += 1
            except ConflictError:
                raise
            except Exception, e:
                failures += 1
                if nofail:
                    LOG.error("Failed migration of %s : %s", path, str(e))
                else:
                    raise

            if count and not (count) % 50:
                LOG.info("%s objects migrated", str(count))
                LOG.debug("non_ghost_count: %s / %s",
                        portal._p_jar._cache.cache_non_ghost_count,
                        portal._p_jar._cache.cache_size)
            if count and not count % 500:
                if commit:
                    LOG.debug("COMMIT")
                    transaction.commit()
                    LOG.debug("DONE")
                else:
                    LOG.debug("SAVEPOINT")
                    transaction.savepoint(optimistic=True)
                    LOG.debug("DONE")
                LOG.debug("non_ghost_count: %s / %s",
                        portal._p_jar._cache.cache_non_ghost_count,
                        portal._p_jar._cache.cache_size)

        EtagSupport.http__refreshEtag = EtagSupport._http__refreshEtag
        LOG.info("%s objects updated", str(successes))
        LOG.info("%s failures", str(failures))
        if failures > successes:
            raise Exception, "Too many failures during %s migration" % method.__name__

        message = "%s objects migrated with %s method" % (", ".join(portal_types), method.__name__)
        LOG.info(message)
        return message

    def reindexContents(self, portal_types, indexes=(),
                        query=None, nofail=True, commit=False, stop_at_count=0):

        def reindex_object(obj, path=None):
            obj.reindexObject(idxs=indexes)

        self.migrateContent(portal_types, reindex_object, query=query,
                            nofail=nofail, commit=commit, stop_at_count=stop_at_count)

    def migrateRoleMappings(self, portal_types,
                            catalogs=('portal_catalog',), reindex=False, commit=False,
                            stop_at_count=0):
        """ update security mappings on objets after workflow definitions changed """

        if type(portal_types) not in (tuple, list):
            portal_types = [portal_types]

        wf_tool = getToolByName(self.portal, "portal_workflow")
        getWorkflowTools = wf_tool.getWorkflowsFor

        def updateObjectRoleMappings(obj, path):
            workflow = getWorkflowTools(obj)[0]
            workflow.updateRoleMappingsFor(obj)
            if reindex:
                obj.reindexObjectSecurity()

        self.migrateContent(portal_types, updateObjectRoleMappings, catalogs=catalogs,
                            commit=commit, stop_at_count=stop_at_count)

        message = "%s mappings updated" % ", ".join(portal_types)
        LOG.info(message)
        return message
