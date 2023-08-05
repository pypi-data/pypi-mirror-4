# -*- coding: utf-8 -*-


def uninstall(portal, reinstall=False):
    """
    launch uninstall profile
    """
    setup_tool = portal.portal_setup
    setup_tool.runAllImportStepsFromProfile('profile-Products.PloneGlossary:uninstall')
