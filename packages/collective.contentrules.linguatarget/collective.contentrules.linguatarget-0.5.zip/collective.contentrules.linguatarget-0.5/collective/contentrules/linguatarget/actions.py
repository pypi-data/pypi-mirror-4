import logging

from Acquisition import aq_inner, aq_parent, aq_base
from OFS.CopySupport import sanity_check
from OFS.SimpleItem import SimpleItem
from OFS.event import ObjectClonedEvent
from OFS.event import ObjectWillBeMovedEvent
from ZODB.POSException import ConflictError
import OFS.subscribers

from zope import schema
from zope.component import adapts
from zope.component.interfaces import IObjectEvent
from zope.event import notify
from zope.formlib import form
from zope.interface import implements, Interface
from zope.lifecycleevent import ObjectCopiedEvent

from zope.app.container.contained import ObjectMovedEvent
from zope.app.container.contained import notifyContainerModified

from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 
from plone.app.contentrules.actions.move import MoveActionExecutor
from plone.app.contentrules.actions.copy import CopyActionExecutor 
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.vocabularies.catalog import SearchableTextSourceBinder

from Products.CMFCore.utils import getToolByName

from collective.contentrules.linguatarget import MessageFactory as _

log = logging.getLogger('collective.contentrules.linguatarget')

class ILinguaMoveAction(Interface):
    """ Interface for the configurable aspects of the linguatarget action.
    """
    move_to_translated_parent = schema.Bool(
            title=_(u"Move the object to the correct language version of " 
                    "the target folder"),
            default=True,
                )

    target_folder = schema.Choice(title=_(u"Target folder"),
                                  description=_(u"As a path relative to the portal root."),
                                  required=True,
                                  source=SearchableTextSourceBinder({'is_folderish' : True},
                                                                    default_query='path:'))

class LinguaMoveAction(SimpleItem):
    """ Note that we must mix in SimpleItem to keep Zope 2 security happy.
    """
    implements(ILinguaMoveAction, IRuleElementData)
    element = "collective.contentrules.linguatarget.LinguaMoveAction"

    move_to_translated_parent = True
    target_folder = ''

    @property
    def summary(self):
        return _(u"The object will be moved to the folder ${folder} "
                "or to it's appropriate language version (if it exists).",
                mapping=dict(folder=self.target_folder))


class ILinguaCopyAction(Interface):
    """ Interface for the configurable aspects of the linguatarget action.
    """
    copy_to_translated_parent = schema.Bool(
            title=_(u"Copy the object to the correct language version of " 
                    "the target folder"),
            default=True,
                )

    target_folder = schema.Choice(title=_(u"Target folder"),
                                  description=_(u"As a path relative to the portal root."),
                                  required=True,
                                  source=SearchableTextSourceBinder({'is_folderish' : True},
                                                                    default_query='path:'))


class LinguaCopyAction(SimpleItem):
    """ Note that we must mix in SimpleItem to keep Zope 2 security happy.
    """
    implements(ILinguaCopyAction, IRuleElementData)
    element = "collective.contentrules.linguatarget.LinguaCopyAction"

    copy_to_translated_parent = True
    target_folder = ''

    @property
    def summary(self):
        return _(u"The object will be copied to the folder ${folder} "
                "or to it's appropriate language version (if it exists).",
                mapping=dict(folder=self.target_folder))


class LinguaMoveActionExecutor(MoveActionExecutor):
    """ """
    implements(IExecutable)
    adapts(Interface, ILinguaMoveAction, IObjectEvent)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        portal_url = getToolByName(self.context, 'portal_url', None)
        if portal_url is None:
            return False
        
        obj = self.event.object
        parent = aq_parent(aq_inner(obj))
        
        path = self.element.target_folder
        if len(path) > 1 and path[0] == '/':
            path = path[1:]
        target = portal_url.getPortalObject().unrestrictedTraverse(str(path), None)

        if target is None:
            self.error(obj, _(u"Target folder ${target} does not exist.", mapping={'target' : path}))
            return False

        if self.element.move_to_translated_parent:
            # Get the translated version
            obj_language = obj.getLanguage()
            if obj_language:
                target = target.getTranslation(obj_language)
            else:
                log.info('getLanguage for %s returns empty string!' % obj.getId())

            
        if target.absolute_url() == parent.absolute_url():
            # We're already here!
            return True
        
        try:
            obj._notifyOfCopyTo(target, op=1)
        except ConflictError:
            raise
        except Exception, e:
            self.error(obj, str(e))
            return False

        # Are we trying to move into the same container that we copied from?
        if not sanity_check(target, obj):
            return False

        old_id = obj.getId()
        new_id = self.generate_id(target, old_id)

        notify(ObjectWillBeMovedEvent(obj, parent, old_id, target, new_id))

        obj.manage_changeOwnershipType(explicit=1)

        try:
            parent._delObject(old_id, suppress_events=True)
        except TypeError:
            # BBB: removed in Zope 2.11
            parent._delObject(old_id)
        
        obj = aq_base(obj)
        obj._setId(new_id)

        try:
            target._setObject(new_id, obj, set_owner=0, suppress_events=True)
        except TypeError:
            # BBB: removed in Zope 2.11
            target._setObject(new_id, obj, set_owner=0)
        obj = target._getOb(new_id)

        notify(ObjectMovedEvent(obj, parent, old_id, target, new_id))
        notifyContainerModified(parent)
        if aq_base(parent) is not aq_base(target):
            notifyContainerModified(target)

        obj._postCopy(target, op=1)
        
        # try to make ownership implicit if possible
        obj.manage_changeOwnershipType(explicit=0)
        
        return True


class LinguaCopyActionExecutor(CopyActionExecutor):
    """ """
    implements(IExecutable)
    adapts(Interface, ILinguaCopyAction, IObjectEvent)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):

        portal_url = getToolByName(self.context, 'portal_url', None)
        if portal_url is None:
            return False
        
        obj = self.event.object
        
        path = self.element.target_folder
        if len(path) > 1 and path[0] == '/':
            path = path[1:]
        target = portal_url.getPortalObject().unrestrictedTraverse(str(path), None)
    
        if target is None:
            self.error(obj, _(u"Target folder ${target} does not exist.", mapping={'target' : path}))
            return False

        if self.element.copy_to_translated_parent:
            # Get the translated version
            obj_language = obj.getLanguage()
            if obj_language:
                target = target.getTranslation(obj_language)
            else:
                log.info('getLanguage for %s returns empty string!' % obj.getId())

        try:
            obj._notifyOfCopyTo(target, op=0)
        except ConflictError:
            raise
        except Exception, e:
            self.error(obj, str(e))
            return False
            
        old_id = obj.getId()
        new_id = self.generate_id(target, old_id)
        
        orig_obj = obj
        obj = obj._getCopy(target)
        obj._setId(new_id)
        
        notify(ObjectCopiedEvent(obj, orig_obj))

        target._setObject(new_id, obj)
        obj = target._getOb(new_id)
        obj.wl_clearLocks()

        obj._postCopy(target, op=0)

        OFS.subscribers.compatibilityCall('manage_afterClone', obj, obj)
        
        notify(ObjectClonedEvent(obj))
        
        return True 


class LinguaMoveAddForm(AddForm):
    """ """
    form_fields = form.FormFields(ILinguaMoveAction)
    form_fields['target_folder'].custom_widget = UberSelectionWidget
    label = _(u"Add a translation aware move action")
    description = _(u"A translation aware move action will move the object to "
                    "the appropriate translation of the provided target folder")
    form_name = _(u"Add translation aware move action")

    def create(self, data):
        a = LinguaMoveAction()
        form.applyChanges(a, self.form_fields, data)
        return a

class LinguaMoveEditForm(EditForm):
    """ """
    form_fields = form.FormFields(ILinguaMoveAction)
    form_fields['target_folder'].custom_widget = UberSelectionWidget
    label = _(u"Edit translation aware move action")
    description = _(u"A translation aware move action will move the object to "
                    "the appropriate translation of the provided target folder")
    form_name = _(u"Edit translation aware move action")

class LinguaCopyAddForm(AddForm):
    """ """
    form_fields = form.FormFields(ILinguaCopyAction)
    form_fields['target_folder'].custom_widget = UberSelectionWidget
    label = _(u"Add a translation aware copy action")
    description = _(u"A translation aware move action will copy the object to "
                    "the appropriate translation of the provided target folder")
    form_name = _(u"Edit translation aware copy action")

    def create(self, data):
        a = LinguaCopyAction()
        form.applyChanges(a, self.form_fields, data)
        return a

class LinguaCopyEditForm(EditForm):
    """ """
    form_fields = form.FormFields(ILinguaCopyAction)
    form_fields['target_folder'].custom_widget = UberSelectionWidget
    label = _(u"Edit translation aware copy action")
    description = _(u"A translation aware move action will copy the object to "
                    "the appropriate translation of the provided target folder")
    form_name = _(u"Add translation aware copy action")


