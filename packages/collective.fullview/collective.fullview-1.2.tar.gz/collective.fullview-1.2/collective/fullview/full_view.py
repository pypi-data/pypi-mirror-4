from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.publisher.interfaces.browser import IBrowserView

class FullViewItem(BrowserView):

    def __init__(self, context, request):
        super(FullViewItem, self).__init__(context, request)
        self.item_type = self.context.portal_type

    @property
    def default_view(self):
        context = self.context
        item_layout = context.getLayout()
        layout = {'Link': 'link_view'}.get(self.item_type, item_layout)
        default_view = context.restrictedTraverse(layout)
        return default_view

    @property
    def item_macros(self):
        default_view = self.default_view
        if IBrowserView.providedBy(default_view):
            # IBrowserView
            return default_view.index.macros
        else:
            # FSPageTemplate
            return default_view.macros

    @property
    def item_url(self):
        context = self.context
        url = context.absolute_url()
        props = getToolByName(context, 'portal_properties')
        use_view_action = props.site_properties.typesUseViewActionInListings
        return self.item_type in use_view_action and '%s/view' % url or url

    @property
    def is_pfg(self):
        # context is a PloneFormGen FormFolder.
        # We have to handle it differently
        return self.item_type == "FormFolder"

    @property
    def pfg_prefix(self):
        pfg_prefix = self.request.get('_pfg_prefix', 0)
        pfg_prefix += 1
        self.request.set('_pfg_prefix', pfg_prefix)
        return '_pfg_prefix_%s' % pfg_prefix

    @property
    def pfg_form(self):
        if not self.is_pfg: return None
        form_view = self.context.restrictedTraverse('@@embedded')
        form_view.prefix = self.pfg_prefix
        return form_view()
