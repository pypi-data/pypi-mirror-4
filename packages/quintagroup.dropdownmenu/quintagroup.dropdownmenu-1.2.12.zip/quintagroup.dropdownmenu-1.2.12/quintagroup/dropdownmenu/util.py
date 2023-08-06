# -*- coding: utf-8 -*-
# Miscellaneous functions to use from inside different parts of this package.

from zope.component import getUtility

from Products.CMFCore.utils import getToolByName

from plone.registry.recordsproxy import RecordsProxy, _marker
from plone.registry.interfaces import IRegistry

from quintagroup.dropdownmenu.interfaces import IDropDownMenuSettings


PROP_MAPPING = {
    'show_content_tabs': 'disable_folder_sections',
    'show_nonfolderish_tabs': 'disable_nonfolderish_sections',
}


def getDropDownMenuSettings(context):
    """Return dropdown menu settings"""
    registry = getUtility(IRegistry)
    return DropDownMenuRecordsProxy(context, registry, IDropDownMenuSettings,
                                    omitted=())


class DropDownMenuRecordsProxy(RecordsProxy):
    """Override a few dropdown menu specific settings to get from portal
    properties instead of taking them from plone.registry components"""

    def __init__(self, context, registry, schema, omitted=()):
        # override initialization to pass context for further purposes;
        # yes, I know, this is badly to depend on context in utilities,
        # but I haven't come up with some better way to proxy
        # plone.registry yet skip __setattr__
        self.__dict__['__context__'] = context
        super(DropDownMenuRecordsProxy, self).__init__(registry, schema,
                                                       omitted)

    def __getattr__(self, name):
        if name not in self.__schema__:
            raise AttributeError(name)
        value = _marker
        if name in ('show_content_tabs', 'show_nonfolderish_tabs'):
            context = self.__context__
            prop_tool = getToolByName(context, 'portal_properties')
            if 'site_properties' in prop_tool.objectIds():
                sheet = prop_tool._getOb('site_properties')
                if sheet.hasProperty(PROP_MAPPING[name]):
                    value = not sheet.getProperty(PROP_MAPPING[name])
        else:
            value = self.__registry__.get(self.__prefix__ + name, _marker)
        if value is _marker:
            value = self.__schema__[name].missing_value
        return value

    def __repr__(self):
        return "<DropDownMenuRecordsProxy for %s>" % \
               self.__schema__.__identifier__
