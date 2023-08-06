# -*- coding: utf-8 -*-
from zope.i18n import translate
from zope.component import getUtility
from zope.schema.interfaces import ITitledTokenizedTerm

from Products.CMFCore.utils import getToolByName

from plone.app.registry.browser import controlpanel
from plone.registry.interfaces import IRegistry

from quintagroup.dropdownmenu.interfaces import IDropDownMenuSettings, _


class DropDownMenuSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IDropDownMenuSettings
    label = _(u"DropDown Menu settings")
    description = _(u"Please enter the options specified")

    def applyChanges(self, data):
        """To save a few fields into portal_properties tool"""
        result = super(DropDownMenuSettingsEditForm, self).applyChanges(data)
        self._settings(data['show_content_tabs'],
                       data['show_nonfolderish_tabs'])
        return result

    def update(self):
        """Also get values for a few fields from portal_properties tool"""
        try:
            super(DropDownMenuSettingsEditForm, self).update()
        except KeyError:
            registry = getUtility(IRegistry)
            registry.registerInterface(self.schema)
            super(DropDownMenuSettingsEditForm, self).update()
        conf = self._settings()
        self._overrideValue(self.widgets['show_content_tabs'], not conf[0])
        self._overrideValue(self.widgets['show_nonfolderish_tabs'],
                            not conf[1])

    def _overrideValue(self, widget, value):
        if value:
            widget.value = ['selected']

        widget.items = []
        for count, term in enumerate(widget.terms):
            checked = widget.isChecked(term)
            id = '%s-%i' % (widget.id, count)
            label = term.token
            if ITitledTokenizedTerm.providedBy(term):
                label = translate(term.title, context=widget.request,
                                  default=term.title)
            widget.items.append({
                'id': id, 'name': widget.name + ':list',
                'value': term.token, 'label': label, 'checked': checked})

    def _settings(self, folder=None, nonfolderish=None):
        """Return portal_properties settings"""
        props = [True, True]
        prop_tool = getToolByName(self.context, 'portal_properties')
        if 'site_properties' in prop_tool.objectIds():
            sheet = prop_tool._getOb('site_properties')
            if sheet.hasProperty('disable_folder_sections'):
                if folder is not None:
                    sheet.manage_changeProperties(
                        disable_folder_sections=not folder)
                props[0] = sheet.getProperty('disable_folder_sections')
            if sheet.hasProperty('disable_nonfolderish_sections'):
                if nonfolderish is not None:
                    sheet.manage_changeProperties(
                        disable_nonfolderish_sections=not nonfolderish)
                props[1] = sheet.getProperty('disable_nonfolderish_sections')
        return props


class DropDownMenuSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = DropDownMenuSettingsEditForm
