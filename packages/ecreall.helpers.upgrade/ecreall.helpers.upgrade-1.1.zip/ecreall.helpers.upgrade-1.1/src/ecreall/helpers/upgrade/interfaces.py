from zope.interface import Interface


class IUpgradeTool(Interface):
    """ utilities on portal setup to pass upgrade steps """

    def refreshResources():
        """ recook all resources (css, js, kss) """

    def runUpgradeSteps(steps):
        """
        @param steps : tuple of pairs (product, version)
        pass upgrade steps of products

        ex: self.passUpgradeSteps((("alter.my.product", "1.0.2"),
                                   ("alter.your.product", "2.5.4")))
        """

    def runUpgradeStep(profile, destination):
        """
        pass step of product profile towards destination
        ex: self.passUpgradeStep("alter.my.product", "1.0.2")
        """

    def runProfile(profile, purge_old=False):
        """Run all steps od a profile
        """

    def runImportStep(profile, importstep):
        """Run one import step of a profile
        """

    def installProduct(product):
        """
        install product
        """

    def uninstallProduct(product):
        """
        uninstall product
        """

    def reinstallProduct(product):
        """
        reinstall product
        """

    def runUpgradeProfile(profile):
        """
        run an upgrade profile
        @param profile : migration profile package + ":" profile name
        ex: self.runUpgradeProfile("conf.site.common.upgrades:v1_3_0")
        """

    def migrateContent(portal_types, method, catalogs=('portal_catalog',),
                       query=None, nofail=True):
        """ apply method on portal_types contents of catalogs """

    def migrateRoleMappings(portal_types,
                            catalogs=('portal_catalog',), reindex=False):
        """ update security mappings on objets after workflow definitions changed """

    def reindexContents(portal_types, indexes=(), nofail=True, commit=False):
        """Reindex all contents of selected types
        """

    def refreshResources():
        """Refresh all resource registries
        """

    def updateIndexes(index_tuples, catalogs=['portal_catalog'], reindex=True):
        """
        add and/or reindex indexes of catalogs
        @param index_tuples list of tuples [(index, index_type)]
        """
