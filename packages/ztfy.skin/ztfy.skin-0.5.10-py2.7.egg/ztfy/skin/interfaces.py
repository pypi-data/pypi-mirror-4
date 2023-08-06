### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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
from z3c.form.interfaces import ISubForm, IWidget, ITextWidget, ITextAreaWidget, INPUT_MODE
from zope.container.interfaces import IContainer
from zope.viewlet.interfaces import IViewlet, IViewletManager

# import local interfaces

# import Zope3 packages
from z3c.form import button
from z3c.formjs import jsaction
from zope.interface import Attribute, Interface
from zope.schema import Bool, TextLine, List, Choice, Dict, Object, Password

# import local packages

from ztfy.skin import _


#
# Skinnable contents
#

class ISkinnable(Interface):
    """Base skinnable contents interface"""

    def getSkin(self):
        """Get real skin applied to context"""


#
# Custom widgets interfaces
#

class IDateWidget(ITextWidget):
    """Marker interface for date widget"""


class IDatetimeWidget(ITextWidget):
    """Marker interface for datetime widget"""


class IFixedWidthTextAreaWidget(ITextAreaWidget):
    """Marker interface for fixed width text area widget"""


#
# Default views interfaces
#

class IDefaultView(Interface):
    """Interface used to get object's default view name"""

    viewname = TextLine(title=_("View name"),
                        description=_("Name of the default view for the adapter object and request"),
                        required=True,
                        default=u'@@index.html')

    def getAbsoluteURL(self):
        """Get full absolute URL of the default view"""


class IContainedDefaultView(IDefaultView):
    """Interface used to get object's default view name while displayed inside a container"""


class IContainerAddFormMenuTarget(Interface):
    """Marker interface for base add form menu item"""


class IPropertiesMenuTarget(Interface):
    """Marker interface for properties menus"""


#
# Containers interfaces
#

class IOrderedContainerOrder(Interface):
    """Ordered containers interface"""

    def updateOrder(self, order):
        """Reset items in given order"""

    def moveUp(self, key):
        """Move given item up"""

    def moveDown(self, key):
        """Move given item down"""

    def moveFirst(self, key):
        """Move given item to first position"""

    def moveLast(self, key):
        """Move given item to last position"""


class IOrderedContainer(IOrderedContainerOrder, IContainer):
    """Marker interface for ordered containers"""


class IContainerBaseView(Interface):
    """Marker interface for container base view"""


class IOrderedContainerBaseView(Interface):
    """Marker interface for ordered container based view"""


class IOrderedContainerSorterColumn(Interface):
    """Marker interface for container sorter column"""


#
# Custom forms interfaces
#

def checkSubmitButton(form):
    """Check form and widgets mode before displaying submit button"""
    if form.mode != INPUT_MODE:
        return False
    for widget in form.widgets.values():
        if widget.mode == INPUT_MODE:
            return True
    if IForm.providedBy(form):
        for subform in form.subforms:
            for widget in subform.widgets.values():
                if widget.mode == INPUT_MODE:
                    return True


class IEditFormButtons(Interface):
    """Default edit form buttons"""

    submit = button.Button(title=_("Submit"), condition=checkSubmitButton)
    reset = button.Button(title=_("Reset"))


class IDialogAddFormButtons(Interface):
    """Default dialog add form buttons"""

    add = jsaction.JSButton(title=_("Add"))
    cancel = jsaction.JSButton(title=_("Cancel"))


class IDialogDisplayFormButtons(Interface):
    """Default dialog display form buttons"""

    dialog_close = jsaction.JSButton(title=_("Close"))


class IDialogEditFormButtons(Interface):
    """Default dialog edit form buttons"""

    dialog_submit = jsaction.JSButton(title=_("Submit"), condition=checkSubmitButton)
    dialog_cancel = jsaction.JSButton(title=_("Cancel"))


class IWidgetsGroup(Interface):
    """Form widgets group interface"""

    id = Attribute(_("Group ID"))

    widgets = List(title=_("Group widgets"),
                   value_type=Object(IWidget))

    cssClass = Attribute(_("CSS class"))

    legend = Attribute(_("Group title"))

    help = Attribute(_("Group help"))

    switch = Bool(title=_("Display group switch ?"),
                  required=True,
                  default=False)

    hide_if_empty = Bool(title=_("Hide group if empty ?"),
                         description=_("""If 'Yes', a switchable group containing only """
                                       """widgets with default values is hidden"""),
                         required=True,
                         default=False)

    visible = Attribute(_("Visible group"))


class IGroupsBasedForm(Interface):
    """Groups based form"""

    groups = Attribute(_("Form groups"))

    def addGroup(self, group):
        """Add given group to form"""


class IBaseForm(Interface):
    """Marker interface for any form"""


class ICustomExtractSubForm(ISubForm):
    """SubForm interface with custom extract method"""

    def extract(self):
        """Extract data and errors from input request"""


class ICustomUpdateSubForm(ISubForm):
    """SubForm interface with custom update method"""

    def updateContent(self, object, data):
        """Update custom content with given data"""


class IForm(Interface):
    """Base form interface"""

    title = TextLine(title=_("Form title"))

    legend = TextLine(title=_("Form legend"),
                      required=False)

    subforms = List(title=_("Sub-forms"),
                    value_type=Object(schema=ISubForm),
                    required=False)

    tabforms = List(title=_("Tab-forms"),
                    value_type=Object(schema=ISubForm),
                    required=False)

    autocomplete = Choice(title=_("Auto-complete"),
                          values=('on', 'off'),
                          default='on')

    display_hints_on_widgets = Bool(title=_("Display hints on input widgets?"),
                                    required=True,
                                    default=False)

    callbacks = Dict(title=_("Widgets callbacks"),
                     key_type=TextLine(),
                     value_type=TextLine())

    def createSubForms(self):
        """Initialize sub-forms"""

    def createTabForms(self):
        """Initialize tab-forms"""

    def getForms(self):
        """Get full list of forms"""

    def getWidgetCallback(self, widget):
        """Get submit callback associated with a given widget"""


class IViewletsBasedForm(IForm):
    """Viewlets based form interface"""

    managers = List(title=_("Names list of viewlets managers included in this form"),
                    value_type=TextLine(),
                    required=True)


class ISubFormViewlet(IViewlet):
    """Sub-form viewlet interface"""

    legend = Attribute(_("Sub-form legend"))

    switchable = Attribute(_("Can the subform be hidden ?"))

    visible = Attribute(_("Is the subform initially visible ?"))

    callbacks = Dict(title=_("Widgets callbacks"),
                     key_type=TextLine(),
                     value_type=TextLine())

    def getWidgetCallback(self, widget):
        """Get submit callback associated with a given widget"""


class IDialog(Interface):
    """Base interface for AJAX dialogs"""

    resources = Attribute(_("List of resources needed by this dialog"))


class IDialogMenu(Interface):
    """Dialog access menu interface"""

    target = Attribute(_("Target dialog class"))


class IDialogTitle(Interface):
    """Dialog title getter interface"""

    def getTitle(self):
        """Get dialog title"""


#
# Default form content providers
#

class IFormViewletsManager(IViewletManager):
    """Base forms viewlets manager interface"""


class IFormPrefixViewletsManager(IFormViewletsManager):
    """Form prefix viewlets manager interface"""


class IWidgetsPrefixViewletsManager(IFormViewletsManager):
    """Form widgets prefix viewlets manager interface"""


class IWidgetsSuffixViewletsManager(IFormViewletsManager):
    """Form widgets suffix viewlets manager interface"""


class IFormSuffixViewletsManager(IFormViewletsManager):
    """Form suffix viewlets manager interface"""


#
# Breadcrumb interfaces
#

class IBreadcrumbInfo(Interface):
    """Get custom breadcrumb info of a given context"""

    visible = Bool(title=_("Visible ?"),
                   required=True,
                   default=True)

    title = TextLine(title=_("Title"),
                     required=True)

    path = TextLine(title=_("Path"),
                    required=False)


#
# Back-office custom properties marker interface
#

class ICustomBackOfficeInfoTarget(Interface):
    """Marker interface for custom back-office properties"""

    back_interface = Attribute(_("Back-office properties custom interface"))


#
# Login form attributes
#

class ILoginFormFields(Interface):
    """Login form fields interface"""

    username = TextLine(title=_("login-field", "Login"),
                        required=True)

    password = Password(title=_("password-field", "Password"),
                        required=True)

    came_from = TextLine(title=_("came-from", "Original address"),
                         required=False)
