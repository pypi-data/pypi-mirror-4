### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces
from z3c.form.interfaces import IActions, IButtonForm, ISubForm, IHandlerForm, IWidgets, \
                                DISPLAY_MODE
from z3c.json.interfaces import IJSONWriter
from z3c.language.switch.interfaces import II18n
from zope.container.interfaces import IContainer
from zope.contentprovider.interfaces import IContentProvider
from zope.dublincore.interfaces import IZopeDublinCore

# import local interfaces
from ztfy.skin.interfaces import IBaseForm, IForm, IDialog, ICustomUpdateSubForm, \
                                 IEditFormButtons, IDialogAddFormButtons, \
                                 IDialogDisplayFormButtons, IDialogEditFormButtons, \
                                 IViewletsBasedForm, ISubFormViewlet, \
                                 IWidgetsGroup, IGroupsBasedForm

# import Zope3 packages
from z3c.form import subform, button
from z3c.formjs import ajax, jsaction
from z3c.formui import form
from zope.component import getMultiAdapter, getUtility, queryMultiAdapter
from zope.event import notify
from zope.i18n import translate
from zope.interface import implements
from zope.lifecycleevent import Attributes, ObjectCreatedEvent, ObjectModifiedEvent
from zope.security.proxy import removeSecurityProxy
from zope.traversing.api import getName

# import local packages
from ztfy.jqueryui import jquery_tools, jquery_progressbar
from ztfy.skin.page import BaseBackView
from ztfy.utils.property import cached_property
from ztfy.utils.traversing import getParent

from ztfy.skin import _


#
# Custom forms base classes
#

class AjaxForm(ajax.AJAXRequestHandler):
    """Custom base form class used to handle AJAX errors
    
    This base class may be combined with other form based classes (form.AddForm or form.EditForm)
    which provide standard form methods
    """

    def getAjaxErrors(self):
        errors = {}
        errors['status'] = translate(self.status, context=self.request)
        for error in self.errors:
            error.update()
            error = removeSecurityProxy(error)
            if hasattr(error, 'widget'):
                widget = removeSecurityProxy(error.widget)
                if widget is not None:
                    errors.setdefault('errors', []).append({ 'id': widget.id,
                                                             'widget': translate(widget.label, context=self.request),
                                                             'message': translate(error.message, context=self.request) })
                else:
                    errors.setdefault('errors', []).append({ 'message': translate(error.message, context=self.request) })
            else:
                errors.setdefault('errors', []).append({ 'message': translate(error.message, context=self.request) })
        return { 'output': u'ERRORS',
                 'errors': errors }


class ViewletsBasedForm(form.Form):
    """Viewlets based form"""

    implements(IViewletsBasedForm)

    managers = []

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.viewlets = []

    @property
    def errors(self):
        result = []
        for viewlet in self.viewlets:
            _data, errors = viewlet.extractData()
            result.extend(errors)
        return tuple(result)

    def updateActions(self):
        super(ViewletsBasedForm, self).updateActions()
        for name in self.managers:
            manager = queryMultiAdapter((self.context, self.request, self), IContentProvider, name)
            if manager is not None:
                manager.update()
                self.viewlets.extend(manager.viewlets)

    def updateContent(self, object, data):
        for subform in self.viewlets:
            subform_data, _errors = subform.extractData()
            form.applyChanges(subform, object, subform_data)


class SubFormViewlet(subform.EditSubForm):
    """Sub-form viewlet"""

    implements(ISubFormViewlet)

    def __init__(self, context, request, parentForm, manager):
        super(SubFormViewlet, self).__init__(context, request, parentForm)
        self.manager = manager

    @property
    def ignoreContext(self):
        return self.parentForm.ignoreContext

    def updateWidgets(self):
        self.widgets = getMultiAdapter((self, self.request, self.getContent()), IWidgets)
        self.widgets.ignoreContext = self.ignoreContext
        self.widgets.update()


#
# Form widgets groups
#

class WidgetsGroup(object):
    """Widgets group class"""

    implements(IWidgetsGroup)

    def __init__(self, id, widgets=(), legend=None, help=None, cssClass='', switch=False, hide_if_empty=False):
        self.id = id
        self.legend = (legend is None) and id or legend
        self.help = help
        self.cssClass = cssClass
        self.switch = switch
        self.hide_if_empty = hide_if_empty
        self.widgets = widgets

    @cached_property
    def visible(self):
        if not (self.switch and self.hide_if_empty):
            return True
        for widget in self.widgets:
            if not widget.ignoreContext:
                field = widget.field
                context = widget.context
                name = field.getName()
                value = getattr(context, name, None)
                if value and (value != field.default):
                    return True
        return False


def NamedWidgetsGroup(id, widgets, names=(), legend=None, help=None, cssClass='', switch=False, hide_if_empty=False):
    """Create a widgets group based on widgets names"""
    return WidgetsGroup(id, [widgets.get(name) for name in names], legend, help, cssClass, switch, hide_if_empty)


class GroupsBasedForm(object):
    """Groups based form"""

    implements(IGroupsBasedForm)

    def __init__(self):
        self._groups = []

    def addGroup(self, group):
        self._groups.append(group)

    @property
    def groups(self):
        result = self._groups[:]
        others = []
        for widget in self.widgets.values():
            found = False
            for group in result:
                if widget in group.widgets:
                    found = True
                    break
            if not found:
                others.append(widget)
        if others:
            result.insert(0, WidgetsGroup(None, others))
        return result


#
# Add forms
#

class BaseAddForm(form.AddForm, GroupsBasedForm):
    """Custom AddForm
    
    This form overrides creation process to allow created contents to be
    'parented' before changes to be applied. This is required for ExtFile
    properties to work correctly.
    """

    implements(IForm, IBaseForm)

    autocomplete = 'on'
    formErrorsMessage = _('There were some errors.')

    def __init__(self, context, request):
        form.AddForm.__init__(self, context, request)
        GroupsBasedForm.__init__(self)

    # override button to get translated label
    @button.buttonAndHandler(_('Add'), name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True

    def update(self):
        jquery_progressbar.need()
        super(BaseAddForm, self).update()
        self.getForms()
        [ subform.update() for subform in self.subforms ]
        [ tabform.update() for tabform in self.tabforms ]

    def updateWidgets(self):
        super(BaseAddForm, self).updateWidgets()
        self.getForms()
        [ subform.updateWidgets() for subform in self.subforms ]
        [ tabform.updateWidgets() for tabform in self.tabforms ]

    def createSubForms(self):
        return []

    def createTabForms(self):
        return []

    def getForms(self):
        if not hasattr(self, 'subforms'):
            self.subforms = [ form for form in self.createSubForms()
                                            if form is not None ]
        if not hasattr(self, 'tabforms'):
            tabforms = self.tabforms = [ form for form in self.createTabForms()
                                                       if form is not None ]
            if tabforms:
                jquery_tools.need()
        return [self, ] + self.subforms + self.tabforms

    @property
    def errors(self):
        result = []
        for subform in self.getForms():
            result.extend(subform.widgets.errors)
        return result

    def createAndAdd(self, data):
        object = self.create(data)
        notify(ObjectCreatedEvent(object))
        self.add(object)
        self.updateContent(object, data)
        return object

    def updateContent(self, object, data):
        form.applyChanges(self, object, data)
        self.getForms()
        for subform in self.subforms:
            if ICustomUpdateSubForm.providedBy(subform):
                ICustomUpdateSubForm(subform).updateContent(object, data)
            else:
                form.applyChanges(subform, object, data)
        for tabform in self.tabforms:
            if ICustomUpdateSubForm.providedBy(tabform):
                ICustomUpdateSubForm(tabform).updateContent(object, data)
            else:
                form.applyChanges(tabform, object, data)


class AddForm(BaseBackView, BaseAddForm):
    """Add form"""

    def update(self):
        BaseBackView.update(self)
        BaseAddForm.update(self)


class AddSubForm(subform.EditSubForm):
    """Add sub-form"""

    def __init__(self, context, request, parentForm):
        super(AddSubForm, self).__init__(None, request, parentForm)

    def updateWidgets(self):
        self.widgets = getMultiAdapter((self, self.request, self.getContent()), IWidgets)
        self.widgets.ignoreContext = True
        self.widgets.update()


class DialogAddForm(AjaxForm, AddForm):
    """Custom AJAX add form dialog"""

    implements(IDialog, IBaseForm)

    buttons = button.Buttons(IDialogAddFormButtons)
    layout = None
    parent_interface = IContainer
    parent_view = None
    handle_upload = False

    @jsaction.handler(buttons['add'])
    def add_handler(self, event, selector):
        return '$.ZTFY.form.add(this.form);'

    @jsaction.handler(buttons['cancel'])
    def cancel_handler(self, event, selector):
        return '$.ZTFY.dialog.close();'

    @ajax.handler
    def ajaxCreate(self):
        # Create resources through AJAX request
        # JSON results have to be included in a textarea to handle JQuery.Form plugin file uploads
        writer = getUtility(IJSONWriter)
        self.updateWidgets()
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return writer.write(self.getAjaxErrors())
        self.createAndAdd(data)
        if self.parent_interface is not None:
            parent = getParent(self.context, self.parent_interface)
            notify(ObjectModifiedEvent(parent))
        else:
            parent = None
        return self.getOutput(writer, parent)

    def getOutput(self, writer, parent):
        if self.parent_view is not None:
            view = self.parent_view(parent, self.request)
            view.update()
            return '<textarea>%s</textarea>' % writer.write({ 'output': u"<!-- OK -->\n" + view.output() })
        else:
            return writer.write({ 'output': u"OK" })


#
# Edit forms
#

class BaseEditForm(form.EditForm, GroupsBasedForm):
    """Custom EditForm"""

    implements(IForm, IBaseForm)

    buttons = button.Buttons(IEditFormButtons)

    autocomplete = 'on'
    formErrorsMessage = _('There were some errors.')
    successMessage = _('Data successfully updated.')
    noChangesMessage = _('No changes were applied.')

    def __init__(self, context, request):
        form.EditForm.__init__(self, context, request)
        GroupsBasedForm.__init__(self)

    def update(self):
        jquery_progressbar.need()
        super(BaseEditForm, self).update()
        self.getForms()
        [ subform.update() for subform in self.subforms ]
        [ tabform.update() for tabform in self.tabforms ]

    def updateWidgets(self):
        super(BaseEditForm, self).updateWidgets()
        self.getForms()
        [ subform.updateWidgets() for subform in self.subforms ]
        [ tabform.updateWidgets() for tabform in self.tabforms ]

    def createSubForms(self):
        return []

    def createTabForms(self):
        return []

    def getForms(self):
        if not hasattr(self, 'subforms'):
            self.subforms = [ form for form in self.createSubForms()
                                            if form is not None ]
        if not hasattr(self, 'tabforms'):
            tabforms = self.tabforms = [ form for form in self.createTabForms()
                                                       if form is not None ]
            if tabforms:
                jquery_tools.need()
        return [self, ] + self.subforms + self.tabforms

    @button.handler(buttons['submit'])
    def submit(self, action):
        super(BaseEditForm, self).handleApply(self, action)

    @jsaction.handler(buttons['reset'])
    def reset(self, event, selector):
        return '$.ZTFY.form.reset(this.form);'

    def applyChanges(self, data):
        content = self.getContent()
        changes = self.updateContent(content, data)
        # ``changes`` is a dictionary; if empty, there were no changes
        if changes:
            # Construct change-descriptions for the object-modified event
            descriptions = []
            for interface, names in changes.items():
                descriptions.append(Attributes(interface, *names))
            # Send out a detailed object-modified event
            notify(ObjectModifiedEvent(content, *descriptions))
        return changes

    def updateContent(self, content, data):
        changes = form.applyChanges(self, content, data)
        self.getForms()
        for subform in self.subforms:
            if ICustomUpdateSubForm.providedBy(subform):
                changes.update(ICustomUpdateSubForm(subform).updateContent(content, data) or {})
            else:
                changes.update(form.applyChanges(subform, content, data))
        for tabform in self.tabforms:
            if ICustomUpdateSubForm.providedBy(tabform):
                changes.update(ICustomUpdateSubForm(tabform).updateContent(content, data) or {})
            else:
                changes.update(form.applyChanges(tabform, content, data))
        return changes

    @property
    def errors(self):
        result = []
        for subform in self.getForms():
            result.extend(subform.widgets.errors)
        return result


class EditForm(BaseBackView, BaseEditForm):
    """Edit form"""

    def update(self):
        BaseBackView.update(self)
        BaseEditForm.update(self)


class EditSubForm(subform.EditSubForm):
    """Custom EditSubForm
    
    Actually no custom code..."""

    tabLabel = None


class DialogEditForm(AjaxForm, EditForm):
    """Base dialog simple edit form"""

    implements(IDialog)

    buttons = button.Buttons(IDialogEditFormButtons)
    layout = None
    parent_interface = IContainer
    parent_view = None
    handle_upload = False

    @property
    def title(self):
        result = None
        i18n = II18n(self.context, None)
        if i18n is not None:
            result = II18n(self.context).queryAttribute('title', request=self.request)
        if result is None:
            dc = IZopeDublinCore(self.context, None)
            if dc is not None:
                result = dc.title
        if not result:
            result = '{{ %s }}' % getName(self.context)
        return result

    @jsaction.handler(buttons['dialog_submit'])
    def submit_handler(self, event, selector):
        return '''$.ZTFY.form.edit(this.form);'''

    @jsaction.handler(buttons['dialog_cancel'])
    def cancel_handler(self, event, selector):
        return '$.ZTFY.dialog.close();'

    @ajax.handler
    def ajaxEdit(self):
        writer = getUtility(IJSONWriter)
        self.updateWidgets()
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return writer.write(self.getAjaxErrors())
        changes = self.applyChanges(data)
        if self.parent_interface is not None:
            parent = getParent(self.context, self.parent_interface)
            if changes:
                notify(ObjectModifiedEvent(parent))
        else:
            parent = None
        return self.getOutput(writer, parent, changes)

    def getOutput(self, writer, parent, changes=()):
        if self.parent_view is not None:
            view = self.parent_view(parent, self.request)
            view.update()
            return '<textarea>%s</textarea>' % writer.write({ 'output': u"<!-- OK -->\n" + view.output() })
        else:
            status = changes and u'OK' or u'NONE'
            return writer.write({ 'output': status })


#
# Display forms
#

class BaseDisplayForm(form.DisplayForm, GroupsBasedForm):
    """Custom DisplayForm"""

    implements(IForm, IBaseForm)

    autocomplete = 'on'
    cssClass = 'display-form'

    def __init__(self, context, request):
        form.DisplayForm.__init__(self, context, request)
        GroupsBasedForm.__init__(self)

    @property
    def name(self):
        """See interfaces.IInputForm"""
        return self.prefix.strip('.')

    @property
    def id(self):
        return self.name.replace('.', '-')

    def update(self):
        super(BaseDisplayForm, self).update()
        self.getForms()
        [ subform.update() for subform in self.subforms ]
        [ tabform.update() for tabform in self.tabforms ]

    def updateWidgets(self):
        super(BaseDisplayForm, self).updateWidgets()
        self.getForms()
        [ subform.updateWidgets() for subform in self.subforms ]
        [ tabform.updateWidgets() for tabform in self.tabforms ]

    def createSubForms(self):
        return []

    def createTabForms(self):
        return []

    def getForms(self):
        if not hasattr(self, 'subforms'):
            self.subforms = [ form for form in self.createSubForms()
                                            if form is not None ]
        if not hasattr(self, 'tabforms'):
            tabforms = self.tabforms = [ form for form in self.createTabForms()
                                                       if form is not None ]
            if tabforms:
                jquery_tools.need()
        return [self, ] + self.subforms + self.tabforms

    @property
    def errors(self):
        result = []
        for subform in self.getForms():
            result.extend(subform.widgets.errors)
        return result


class DisplayForm(BaseBackView, BaseDisplayForm):
    """Display form"""

    def update(self):
        BaseBackView.update(self)
        BaseDisplayForm.update(self)


class DisplaySubForm(form.DisplayForm):
    """Custom display sub-form"""

    implements(IForm, ISubForm, IHandlerForm)

    autocomplete = 'on'
    cssClass = 'display-form'

    tabLabel = None
    mode = DISPLAY_MODE

    def __init__(self, context, request, parentForm):
        self.context = context
        self.request = request
        self.parentForm = self.__parent__ = parentForm


class DialogDisplayForm(AjaxForm, DisplayForm):
    """Custom AJAX display dialog base class"""

    implements(IDialog, IButtonForm)

    buttons = button.Buttons(IDialogDisplayFormButtons)

    @property
    def title(self):
        result = None
        i18n = II18n(self.context, None)
        if i18n is not None:
            result = II18n(self.context).queryAttribute('title', request=self.request)
        if result is None:
            dc = IZopeDublinCore(self.context, None)
            if dc is not None:
                result = dc.title
        if not result:
            result = '{{ %s }}' % getName(self.context)
        return result

    def update(self):
        super(DialogDisplayForm, self).update()
        self.updateActions()

    def updateActions(self):
        self.actions = getMultiAdapter((self, self.request, self.getContent()),
                                       IActions)
        self.actions.update()

    @jsaction.handler(buttons['dialog_close'])
    def close_handler(self, event, selector):
        return '$.ZTFY.dialog.close();'
