from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from slc.linkcollection.browser.viewlets import LinkBoxViewlet


class LinkcollectionView(LinkBoxViewlet):
    """View for displaying the contents of a Linkcollection, e.g. on a folder
    """
    template = ViewPageTemplateFile('linkcollection_view.pt')

    def __call__(self):
        return self.template()
