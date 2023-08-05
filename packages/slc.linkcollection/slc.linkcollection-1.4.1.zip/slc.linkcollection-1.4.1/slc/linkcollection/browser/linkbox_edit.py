#from z3c.form import form, field, button
#from plone.z3cform.layout import wrap_form
from DateTime import DateTime
from persistent import Persistent

from zope.app.component.hooks import getSite
from zope.annotation import factory
from zope.component import adapts
from zope.formlib import form
from zope.interface import implements

from Products.ATContentTypes.interface import IATDocument, IATFolder
from Products.CMFCore.utils import getToolByName

from plone.app.form.widgets.uberselectionwidget import UberMultiSelectionWidget

from slc.linkcollection.interfaces import ILinkList
from slc.linkcollection.interfaces import ILinkListDocument
from slc.linkcollection.interfaces import ILinkListFolder
from slc.linkcollection import LinkCollectionMessageFactory as _


class LinkListBase(Persistent):
    implements(ILinkList)

    @property
    def portal_catalog(self):
        """Make the adapter penetratable for the vocabulary to find the cat"""
        return getToolByName(getSite(), 'portal_catalog')

    @property
    def portal_url(self):
        """Make the adapter penetratable for the vocabulary to find the cat"""
        return getToolByName(getSite(), 'portal_url')

    urls = []


class LinkList(LinkListBase):
    implements(ILinkList, ILinkListDocument)
    adapts(IATDocument)

linklist_adapter_document = factory(LinkList)


class LinkListFolder(LinkListBase):
    implements(ILinkList, ILinkListFolder)
    adapts(IATFolder)

linklist_adapter_folder = factory(LinkListFolder)


class LinkCollectionForm(form.PageEditForm):
    form_fields = form.Fields(ILinkList)
    label = u"Add Content Objects to point to"
    form_fields['urls'].custom_widget = UberMultiSelectionWidget

    @form.action(_("Apply"))
    def handle_edit_action(self, action, data):
        ILinkList(self.context).urls = data['urls']

        status = _("Updated on ${date_time}",
                   mapping={'date_time': DateTime()}
                   )
        self.status = status

LinkCollectionView = LinkCollectionForm
