# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import safe_unicode
from zope.app.component.hooks import getSite

from Products.ATContentTypes.interface import IATDocument, IATFolder
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets import common

from slc.linkcollection.interfaces import ILinkList
from types import *


class LinkBoxViewlet(common.ViewletBase):

    render = ViewPageTemplateFile('linkbox.pt')

    def showeditbox(self):
        user = getToolByName(
            self.context, 'portal_membership').getAuthenticatedMember()
        if user.has_permission('Modify portal content', self.context):
            return True
        return False

    def show(self):
        user = getToolByName(
            self.context, 'portal_membership').getAuthenticatedMember()
        if (not IATDocument.providedBy(self.context)
            and not IATFolder.providedBy(self.context)):
            return False
        if user.has_permission('Modify portal content', self.context):
            return True
        if self.links() != []:
            return True
        return False

    def name_item(self, link):
        idx = self.links().index(link)
        return 'linklist-item-%s' % idx

    def raw(self):
        if (not IATDocument.providedBy(self.context)
            and not IATFolder.providedBy(self.context)):
            return []
        urls = ILinkList(self.context).urls
        return urls

    def links(self):
        if (not IATDocument.providedBy(self.context)
            and not IATFolder.providedBy(self.context)):
            return []
        urls = ILinkList(self.context).urls
        if not urls:
            return []
        portal = getSite()
        maps = []
        if type(urls) not in (ListType, TupleType):
            urls = [urls]
        for url in urls:
            if url.startswith('/'):
                url = url[1:]
            ob = portal.restrictedTraverse(url, None)

            if ob is not None:
                maps.append(dict(title=ob.Title(), url=url, uid=ob.UID()))

        return maps

    def docs(self, links=None):
        """ Return the Pages (IATDocument) being linked to.
        """
        docs = []
        links = links or self.links()
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        for link in links:
            doc = portal.restrictedTraverse(link['url'], None)
            if doc is not None:
                docs.append(doc)
        return docs

    def docbody(self, doc):
        """ Return the document's contents as html
        """
        title = safe_unicode(doc.Title(), 'utf-8')
        description = safe_unicode(doc.Description(), 'utf-8')
        bodytext = safe_unicode(doc.getText(), 'utf-8')
        text = """<h1 class="documentFirstHeading">%s</h1>
                  <div class="documentDescription">%s</div>%s
                """ % (title, description, bodytext)
        return text

    def getLink(self):
        context = self.context
        link = context.REQUEST.get('ACTUAL_URL') + \
            (context.REQUEST.get('QUERY_STRING')
             and '?' + context.REQUEST.get('QUERY_STRING') or '')
        return link
