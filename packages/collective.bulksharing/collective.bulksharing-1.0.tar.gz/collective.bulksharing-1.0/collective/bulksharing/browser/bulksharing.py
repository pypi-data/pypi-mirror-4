from Acquisition import aq_inner
from zExceptions import Forbidden

from zope.component import getMultiAdapter

from plone.memoize.instance import memoize
from plone.app.workflow.browser.sharing import STICKY
from plone.app.content.browser.tableview import Table as BaseTable

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.utils import pretty_title_or_id
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from collective.bulksharing import PloneMessageFactory as _


class Table(BaseTable):
    """Simple table for template override."""

    render = ViewPageTemplateFile("table.pt")


class BulkSharingView(BrowserView):
    """ View that allows you to apply bulk role sharing."""

    template = ViewPageTemplateFile('bulksharing.pt')

    STICKY = STICKY

    def __init__(self, context, request):
        super(BulkSharingView, self).__init__(context, request)
        self.objects = [getattr(context, item_path.split('/')[-1])
                        for item_path in self.request.get("paths", [])]
        self.table = SelectedItemsTable(context, request, self.objects)
        self.views = map(self.get_sharing_view, self.objects)


    def get_sharing_view(self, context=None):
        """ Returns sharing view object for specified context.

        If context isn't specified, returns sharing view for
        current context.

        """

        if not context:
            context = self.context

        return getMultiAdapter((context, self.request), name='sharing')

    def __call__(self):
        postback = True

        form = self.request.form
        submitted = form.get('form.submitted', False)
        cancel_button = form.get('form.button.Cancel', None) is not None

        if submitted and not cancel_button:

            if not self.request.get('REQUEST_METHOD', 'GET') == 'POST':
                raise Forbidden

            authenticator = \
                    self.context.restrictedTraverse('@@authenticator', None)
            if not authenticator.verify():
                raise Forbidden

            inherit = bool(form.get('inherit', False))

            reindex = {}
            reindex.update( \
                dict([(v.context.getId(), v) for v in self.views
                    if v.update_inherit(inherit, reindex=False)]))

            entries = form.get('entries', [])
            roles = [r['id'] for r in self.roles()]
            settings = []
            for entry in entries:
                settings.append(dict(id = entry['id'],
                                     type = entry['type'],
                                     roles = [r for r in roles
                                              if entry.get('role_%s' % r,
                                                           False)]))
            if settings:
                reindex.update( \
                    dict([(v.context.getId(), v) for v in self.views
                        if v.update_role_settings(settings, reindex=False)]))

            if reindex:
                for context_id, view in reindex.items():
                    view.context.reindexObjectSecurity()
            IStatusMessage(self.request).addStatusMessage(_(u"Changes saved."),
                                                          type='info')

        if cancel_button:
            postback = False

        if postback:
            return self.template()
        else:
            context_state = \
                self.context.restrictedTraverse("@@plone_context_state")
            url = context_state.view_url()
            self.request.response.redirect(url)
        return self.template()

    def roles(self):
        return self.get_sharing_view().roles()

    def _is_role_settings_equal(self, first, second):
        if set(first.keys()) ^ set(second.keys()):
            return False

        for principal in first:
            fs, ss = first[principal].copy(), second[principal].copy()
            fs['roles'] = tuple(fs['roles'].items())
            ss['roles'] = tuple(ss['roles'].items())
            if set(fs.items()) ^ set(ss.items()):
                return False

        return True

    @memoize
    def role_settings(self):
        available_roles = [(r['id'], False )for r in self.roles()]
        default_settings = [dict(id = STICKY[0],
                                 type = 'group',
                                 title = _(u'Logged-in users'),
                                 disabled = False,
                                 roles = dict(available_roles))]
        if self.views:
            settings = [view.role_settings() for view in self.views]
            principal_settings_map = (dict([(p_settings['id'], p_settings)
                                             for p_settings in view_settings])
                                             for view_settings in settings)

            try:
                first = next(principal_settings_map)
                if all(self._is_role_settings_equal(first, rest)
                        for rest in principal_settings_map):
                    return settings[0]
                else:
                    return default_settings
            except StopIteration:
                return settings[0]
        return default_settings

    def inherited(self):
        if not any(v.inherited() for v in self.views):
            return False
        return True

    def items_table(self):
        return self.table.render()


class SelectedItemsTable(object):
    """Constructs table for selected items."""

    def __init__(self, context, request, objects):
        self.context = context
        self.request = request
        self.objects = objects

        url = context.absolute_url()
        view_url = url + '/@@bulksharing'
        self.table = Table(request, url, view_url, self.items,
                           show_size_column=False, show_modified_column=False,
                           show_status_column=False)
        self.table._selectcurrentbatch = True
        self.table.selectall = True
        self.table.show_all = True

    @property
    def items(self):
        context = aq_inner(self.context)
        plone_utils = getToolByName(context, 'plone_utils')

        items=[]
        for i, obj in enumerate(self.objects):
            title_or_id = pretty_title_or_id(plone_utils, obj)
            items.append(dict(path='/'.join(obj.getPhysicalPath()),
                              obj=obj,
                              id=obj.getId(),
                              title_or_id=safe_unicode(title_or_id),
                              view_url='%s/@@sharing' % obj.absolute_url(),
                              table_row_class= \
                                      (i + 1) % 2 == 0 and "even" or "odd"))

        return items

    def render(self):
        return self.table.render()

