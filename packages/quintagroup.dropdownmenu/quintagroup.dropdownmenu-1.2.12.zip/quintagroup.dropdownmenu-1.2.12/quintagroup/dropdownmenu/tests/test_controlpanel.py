# -*- coding: utf-8 -*-
import unittest
from plone.registry import Registry

from base import TestCase
from base import IPREFIX

from Products.CMFCore.utils import getToolByName
from quintagroup.dropdownmenu.interfaces import IDropDownMenuSettings


class RegistryTest(TestCase):

    def afterSetUp(self):
        # Set up the registry
        super(RegistryTest, self).afterSetUp()
        self.registry = Registry()
        self.registry.registerInterface(IDropDownMenuSettings)

    def test_dropdownmenu_in_controlpanel(self):
        # Check if dropdownmenu is in the control panel
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.failUnless('dropdownmenu' in [
            a.getAction(self)['id']
            for a in self.controlpanel.listActions()])

    def test_show_icons(self):
        # Check show_icons record
        self.registry.records[IPREFIX + 'show_icons']

        self.failUnless('show_icons' in IDropDownMenuSettings)
        self.assertEquals(self.registry[IPREFIX + 'show_icons'], False)

    def test_show_content_tabs(self):
        # Check show_content_tabs record
        self.registry.records[IPREFIX + 'show_content_tabs']

        self.failUnless('show_content_tabs' in IDropDownMenuSettings)
        self.assertEquals(self.registry[IPREFIX + 'show_content_tabs'], True)

    def test_show_nonfolderish_tabs(self):
        # Check show_nonfolderish_tabs record
        self.registry.records[IPREFIX + 'show_nonfolderish_tabs']

        self.failUnless('show_nonfolderish_tabs' in IDropDownMenuSettings)
        self.assertEquals(self.registry[IPREFIX + 'show_nonfolderish_tabs'],
                          True)

    def test_content_before_actions_tabs(self):
        # Check content_before_actions_tabs record
        self.registry.records[IPREFIX + 'content_before_actions_tabs']

        self.failUnless('content_before_actions_tabs' in IDropDownMenuSettings)
        self.assertEquals(self.registry[
            IPREFIX + 'content_before_actions_tabs'], False)

    def test_content_tabs_level(self):
        # Check content_tabs_level record
        self.registry.records[IPREFIX + 'content_tabs_level']

        self.failUnless('content_tabs_level' in IDropDownMenuSettings)
        self.assertEquals(self.registry[IPREFIX + 'content_tabs_level'], 0)

    def test_show_actions_tabs(self):
        # Check show_actions_tabs record
        self.registry.records[IPREFIX + 'show_actions_tabs']

        self.failUnless('show_actions_tabs' in IDropDownMenuSettings)
        self.assertEquals(self.registry[IPREFIX + 'show_actions_tabs'], True)

    def test_actions_tabs_level(self):
        # Check actions_tabs_level record
        self.registry.records[IPREFIX + 'actions_tabs_level']

        self.failUnless('actions_tabs_level' in IDropDownMenuSettings)
        self.assertEquals(self.registry[IPREFIX + 'actions_tabs_level'], 0)

    def test_actions_category(self):
        # Check actions_category record
        self.registry.records[IPREFIX + 'actions_category']

        self.failUnless('actions_category' in IDropDownMenuSettings)
        self.assertEquals(self.registry[IPREFIX + 'actions_category'],
                          u"portal_tabs")

    def test_nested_category_prefix(self):
        # Check nested_category_prefix record
        self.registry.records[IPREFIX + 'nested_category_prefix']

        self.failUnless('nested_category_prefix' in IDropDownMenuSettings)
        self.assertEquals(self.registry[IPREFIX + 'nested_category_prefix'],
                          u"")

    def test_nested_category_sufix(self):
        # Check nested_category_sufix record
        self.registry.records[IPREFIX + 'nested_category_sufix']

        self.failUnless('nested_category_sufix' in IDropDownMenuSettings)
        self.assertEquals(self.registry[IPREFIX + 'nested_category_sufix'],
                          u"_sub")


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
