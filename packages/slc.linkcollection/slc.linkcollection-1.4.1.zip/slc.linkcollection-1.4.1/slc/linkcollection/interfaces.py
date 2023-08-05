from plone.app.vocabularies.catalog import SearchableTextSource, parse_query
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from Products.ATContentTypes.interface import IATDocument
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.ZCTextIndex.ParseTree import ParseError
from zope import schema
from zope.app.component.hooks import getSite
from zope.interface import Interface


class ILinkCollectionLayer(Interface):
    """A layer specific to LinkCollection"""


class ILinkListDocument(Interface):
    """Marker interface for Linklists on documents"""


class ILinkListFolder(Interface):
    """Marker interface for Linklists on folders"""


class LocalSearchableTextSource(SearchableTextSource):
    """Overriding the search method since it adds the current path to the
    results even though it may be a Folder.
    """

    def __init__(self, context, base_query={}, default_query=None):
        super(LocalSearchableTextSource,
              self).__init__(context,
                             base_query=base_query,
                             default_query=default_query)

    def search(self, query_string):
        query = self.base_query.copy()
        if query_string == '':
            if self.default_query is not None:
                query.update(parse_query(self.default_query, self.portal_path))
            else:
                return []
        else:
            query.update(parse_query(query_string, self.portal_path))
        try:
            results = (x.getPath()[len(self.portal_path):]
                       for x in self.catalog(**query))
        except ParseError:
            return []
        return results


class LocalSearchableTextSourceBinder(SearchableTextSourceBinder):
    """ make the binder search in the local folder first """

    def __call__(self, context):
        portal_url = getToolByName(context, 'portal_url', None)
        site = getSite()
        if IPloneSiteRoot.providedBy(site):
            if ILinkListFolder.providedBy(context):
                idx = 0
            else:
                idx = 1
            current_path = '/' + '/'.join(
                portal_url.getRelativeContentPath(site.REQUEST.PARENTS[idx])
            )
            self.default_query = 'path:%s' % current_path
        else:
            self.default_query = 'path:'
        return LocalSearchableTextSource(context, base_query=self.query.copy(),
                                    default_query=self.default_query)


class ILinkList(Interface):
    urls = schema.List(
        title=u"Referenced Documents",
        description=\
u"""Search and select the documents you want to add to your
linklist. The first box contains your current selection. Below it you
can do a fulltext search for documents. Below the search are the
search results you can pic from. Initially they show the contents of
the current folder.""",
            required=True,
            value_type=schema.Choice(
                        title=u"Add documents for referencing",
                        source=LocalSearchableTextSourceBinder(
                            {'object_provides': IATDocument.__identifier__}
                        )
            )
    )
