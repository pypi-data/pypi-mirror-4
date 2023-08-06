# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName


def upgrade1to2(context):
    setup_tool = getToolByName(context, "portal_setup")
    setup_tool.runAllImportStepsFromProfile(
        "profile-maahinkainen.portlet.googlecalendar:upgrade1to2")

    return u"Upgraded maahinkainen.portlet.googlecalendar from 1 to 2."
