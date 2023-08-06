#!/usr/bin/python

"""Run (install and) uninstall steps for this package."""

from Products.CMFCore.utils import getToolByName


def uninstall(portal):
    """Run uninstall steps.

    :param portal: navigation root
    :type portal: Portal object
    :rtype: string
    :returns: static string on success
    """
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile(
        'profile-niteoweb.aweber:uninstall'
    )
    return "Ran all uninstall steps."
