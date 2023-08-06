# -*- coding: utf-8 -*-
from zope import schema
from zope.interface import Interface

from plone.theme.interfaces import IDefaultPloneLayer
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from quintagroup.dropdownmenu import _

cachings = SimpleVocabulary(
    [SimpleTerm(value=u'anonymous', title=_(u'Cache only for anonymous')),
     SimpleTerm(value=u'all', title=_(u'Cache for all users')), ]
)


class IDropDownMenuLayer(IDefaultPloneLayer):
    """Request marker installed via browserlayer.xml.
    """


class IDropDownMenuSettings(Interface):
    """Global dropdown menu settings. This describes records stored in the
    configuration registry and obtainable via plone.registry.
    """

    show_icons = schema.Bool(
        title=_(u"Show tabs icons"),
        description=_(u"Use this setting to switch on/off icons for menu "
                      u"items."),
        default=False)

    show_content_tabs = schema.Bool(
        title=_(u"Show navigation strategy based dropdown menu"),
        description=_(u"Use this setting to switch on/off navigation "
                      u"strategy built dropdown menu"),
        default=True)

    show_nonfolderish_tabs = schema.Bool(
        title=_(u"Show non-folderish menu items"),
        description=_(u"Use this setting to switch on/off non-folderish "
                      u"objects in navigation strategy based dropdown menu"),
        default=True)

    content_before_actions_tabs = schema.Bool(
        title=_(u"Show content tabs before portal_actions tabs"),
        description=_(u""),
        default=False)

    content_tabs_level = schema.Int(
        title=_(u"Navigation strategy dropdown menu depth"),
        description=_(u"How many levels folders to list after the "
                      u"top level."),
        default=0)

    show_actions_tabs = schema.Bool(
        title=_(u"Show actions tabs"),
        description=_(u"Use this setting to enable/disable portal_actions "
                      u"based dropdown menu"),
        default=True)

    actions_tabs_level = schema.Int(
        title=_(u"Actions dropdown menu depth"),
        description=_(u"How many levels of portal_actions to list after the "
                      u"top level."),
        default=0)

    actions_category = schema.TextLine(
        title=_(u"Root portal actions category"),
        description=_(u"Root category id of portal_actions based dropdown "
                      u"menu tree"),
        default=u"portal_tabs")

    nested_category_prefix = schema.TextLine(
        title=_(u"Nested category prefix"),
        description=_(u"Prefix of category id, used to bind category "
                      u"with action"),
        default=u"",
        required=False)

    nested_category_sufix = schema.TextLine(
        title=_(u"Nested category sufix"),
        description=_(u"Sufix of category id, used to bind category "
                      u"with action"),
        default=u"_sub",
        required=False)

    enable_caching = schema.Bool(
        title=_(u"Enable menu caching"),
        description=_(u"Caching of the menu viewlet improves page rendering "
                      u"speed."),
        default=True)

    caching_strategy = schema.Choice(
        title=_(u"Select caching strategy"),
        description=_(u"Caching strategy defines how the cache key will be "
                      u"built."),
        default="anonymous",
        vocabulary=cachings)

    mobile_menu = schema.Bool(
        title=_(u"Display menu as select for small screens"),
        description=_(u"Use select tag to display menu for small screens"),
        default=False)
