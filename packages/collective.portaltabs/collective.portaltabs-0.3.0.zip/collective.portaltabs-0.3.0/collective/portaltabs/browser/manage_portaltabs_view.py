# -*- coding: utf-8 -*-

from elementtree import ElementTree

from Acquisition import aq_inner
from zope.component import getMultiAdapter, queryUtility

from plone.memoize.instance import memoize
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from Products.CMFCore.ActionInformation import Action
from Products.CMFPlone.utils import getFSVersionTuple

from plone.registry.interfaces import IRegistry

from collective.portaltabs import messageFactory as _
from collective.portaltabs.interfaces import IPortalTabsSettings


def _prettify(url_expr):
    if url_expr and not url_expr.startswith('python:') and not url_expr.startswith('string:'):
        return 'tal:' + url_expr
    if url_expr.startswith('string:${globals_view/navigationRootUrl}'):
        if len(url_expr)==40:
            return '/'
        return url_expr[40:]
    if url_expr.startswith('string:'):
        return url_expr[7:]
    return url_expr


def _tallify(url):
    """
    Restore the TAL expression state of the url_expr
    """
    if url.startswith('tal:'):
        return url[4:]
    if url.startswith('www.'):
        url = 'http://' + url
    if url.startswith('/'):
        if url=='/':
            return 'string:${globals_view/navigationRootUrl}'
        return 'string:${globals_view/navigationRootUrl}' + url
    if not url.startswith('string:') and not url.startswith('python:'):
        return 'string:' + url
    return url


def _serialize_category_tabs(category):
    for action in category.values():
        yield {
                'id': action.id,
                'title': action.title,
                'url': _prettify(action.getProperty('url_expr', '')),
                'visible': action.getProperty('visible', False),
                }



class ManagePortaltabsView(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.saveRequest = {}
        self.addRequest = {}
        self.confirmMessage = ''
        # will be {action_id: {data}, ...}
        self.errs = {}
        self.portal_actions = getToolByName(context, 'portal_actions')
        self.translation_service = getToolByName(context, 'translation_service')
        self.plone_utils = getToolByName(context, 'plone_utils')


    def __call__(self):
        request = self.request
        request.set('disable_border', True)
        fn = None
        msg = None
        
        self._handleRequest(request)

        form = request.form
        if form.get('Save'):
            fn = self.form_save
        elif form.get('Add'):
            fn = self.form_add
        elif request.get('Delete'):
            fn = self.form_delete
        elif request.get('move'):
            fn = self.form_move
        elif request.get('Upload'):
            fn = self.form_upload

        if fn:
            msg = fn()

        if msg:
            self.plone_utils.addPortalMessage(msg, type='info')
            request.response.redirect('%s/@@%s' % (self.context.absolute_url(), self.__name__))
        else:
            return self.index()


    def translate(self, msgid, default):
        return self.translation_service.utranslate(domain = 'collective.portaltabs',
                                                   msgid = msgid,
                                                   default = default,
                                                   context = self.context)


    @property
    def confirm_message(self):
        if not self.confirmMessage:
            _ = self.translate
            self.confirmMessage = _(u'confirm_message', default=u'Confirm deletion?')
        return self.confirmMessage


    def iter_categories(self):
        """
        Generate (id, title) tuples of the managed categories.
        Non-existing categories are ignored
        """
        category_ids = self.portal_actions.keys()
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IPortalTabsSettings, check=False)
        categories = []
        for record in settings.manageable_categories:
            id = record.category_id
            title = record.category_title
            # Be sure that the CMF Category exists
            if id in category_ids:
                categories.append( (id, title) )
        return categories


    @memoize
    def iter_translated_categories(self):
        """
        Generate (id, translated_title) tuples of managed categories
        """
        return [(x[0], self.translate(msgid=x[1], default=x[1])) for x in self.iter_categories()]


    @property
    def defaults(self):
        results = []
        for id, title in self.iter_translated_categories():
            results.append({'id': id, 'title': title})
        return results


    @property
    def check_disableFolderSections(self):
        """
        Check if the disable_folder_sections is on or off
        """
        return getToolByName(self.context, 'portal_properties').site_properties.disable_folder_sections


    @property
    def saved_actions(self):
        """
        Return current saved tabs
        """
        results = []
        for category_id, title in self.iter_translated_categories():
            results.append({'id': category_id, 'title': title,
                            'tabs': list(_serialize_category_tabs(self.portal_actions[category_id]))})
        return results


    def getTabs(self, category_id):
        """Obtain tab for a given category"""
        for x in self.saved_actions:
            if category_id==x['id']:
                return x
        return {}


    def _validateInput(self, form):
        """
        Validate possible form input
        """
        errors = {}
        if not form.get('title'):
            errors['title'] = _(u'Title field is required, please provide it.')
        url = form.get('url')
        if not url:
            errors['url'] = _(u'URL field is required, please provide it.')
        else:
            context = aq_inner(self.context)
            portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
            member = portal_state.member()
            if (url.startswith('tal:') or url.startswith('python:')) and \
                    not member.has_permission("collective.portaltabs: Use advanced expressions", portal_state.portal()):
                errors['url'] = _('adv_expression_permission_denied_msg',
                                  default=u'You have no permission to handle expressions like "tal:" or "python:".')
            if url.find('$')>-1 and not \
                    member.has_permission("collective.portaltabs: Use advanced expressions", portal_state.portal()):
                errors['url'] = _('tales_expression_permission_denied_msg',
                                  default=u'You have no permission to handle TALES expressions in static links.')


        return errors


    def form_add(self):
        form = self.request.form
        errors = self._validateInput(form)
        if errors:
            self.errs['__add__'] = errors 
            return None

        category_id = form.get('action')
        title = form.get('title')
        action_id = form.get('id') or self.plone_utils.normalizeString(title)
        action = Action(action_id,
                        title=title,
                        url_expr=_tallify(form.get('url')),
                        permissions=(permissions.View,))
        self.portal_actions[category_id]._setObject(action_id, action)
        return _(u'Tab added')


    def form_save(self):
        form = self.request.form
        visible = form.get('visible')

        params = zip(form.get('id', []),
                     form.get('title', []),
                     form.get('url', []))

        stop = False
        for x in params:
            errors = self._validateInput({'id': x[0], 'title': x[1], 'url': x[2]})
            if errors:
                self.errs[x[0]] = errors 
                stop = True
        if stop:
            return None
        
        for cat_action_id, title, url in params:
            category_id, action_id = cat_action_id.split('|')
            action = self.portal_actions[category_id][action_id]
            action.manage_changeProperties(title = title,
                                           url_expr = _tallify(url),
                                           visible = cat_action_id in visible)
        return _(u'Changes saved')


    def form_delete(self):
        ids = [self.request.get('Delete')]
        category_id = self.request.get('action')
        self.portal_actions[category_id].manage_delObjects(ids=ids)
        return _(u'Tab deleted')


    def form_upload(self):
        """Upload an action.xml compatible file"""
        fin = self.request.form['file']
        tree = ElementTree.parse(fin)

        managed_categories = set(x[0] for x in self.iter_categories())

        for el in tree.findall('object'):
            if el.get('meta_type') != 'CMF Action Category':
                continue

            category_id = el.get('name')
            if category_id not in managed_categories:
                continue

            existing_category = self.portal_actions[category_id]

            for action in el.findall('object'):
                if action.get('meta_type') != 'CMF Action':
                    continue

                action_id = action.get('name')

                props = {}
                permissions = []
                for prop_el in action:
                    name = prop_el.get('name')
                    if name == 'permissions':
                        permissions = [perm.get('value') for perm in prop_el.findall('element')]
                    else:
                        props[name] = prop_el.text or ''

                if action_id in existing_category:
                    action = self.portal_actions[category_id][action_id]
                    action.manage_changeProperties(title=props['title'],
                                                   description=props['description'],
                                                   url_expr=props['url_expr'],
                                                   icon_expr=props['icon_expr'],
                                                   available_expr=props['available_expr'],
                                                   permissions=permissions,
                                                   visible=(props['visible']=='True'),
                                                   )
                else:
                    action = Action(action_id,
                                    title=props['title'],
                                    description=props['description'],
                                    url_expr=props['url_expr'],
                                    icon_expr=props['icon_expr'],
                                    available_expr=props['available_expr'],
                                    permissions=permissions,
                                    visible=(props['visible']=='True'))
                    self.portal_actions[category_id]._setObject(action_id, action)
        return _(u'File uploaded')


    def form_move(self):
        """Move a tab up or down (means left or right commonly)"""
        action_id = self.request.get('move')
        where = self.request.get('where')
        category_id = self.request.get('action')
        category = self.portal_actions[category_id]

        if where == 'top':
            category.moveObjectsToTop(ids=[action_id])
        elif where == 'up':
            category.moveObjectsUp(ids=[action_id])
        elif where == 'down':
            category.moveObjectsDown(ids=[action_id])
        elif where == 'bottom':
            category.moveObjectsToBottom(ids=[action_id])
        else:
            raise ValueError('Bad arguments for moveTab')

        return _(u'Tab moved')


    @property
    def check_canManageNavigationSettings(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        member = portal_state.member()
        plone_version_tuple = getFSVersionTuple() 
        if plone_version_tuple[0]>=4 and plone_version_tuple[1]>=1:
            # If on Plone 4.1 or better we need to check "Plone Site Setup: Navigation" instead of "Manage portal"
            return member.has_permission("Plone Site Setup: Navigation", portal_state.portal())
        return member.has_permission("Manage portal", portal_state.portal())


    @property
    def check_canPortalTabSettings(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        member = portal_state.member()
        return member.has_permission("collective.portaltabs: Manage action categories", portal_state.portal())


    def canSeeRow(self, tab):
        """Check if the current user can see one of the table's row.
        If the row contains a dangerous expressions, check if he can handle data containing
        tal: or python:"""
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        member = portal_state.member()
        if not member.has_permission("collective.portaltabs: Use advanced expressions", portal_state.portal()) \
                and (tab['url'].startswith('python:') or tab['url'].startswith('tal:')):
            return False
        if not member.has_permission("collective.portaltabs: Use advanced expressions", portal_state.portal()) \
                and tab['url'].find('$')>-1:
            return False
        return True


    def _handleRequest(self, request):
        """manage request, to be used in the template for validation errors
        """
        # User pressed the Add button
        if request.get('form.submit.edit'):
            for category_id in request.get('action', []):
                tabs = self.getTabs(category_id)['tabs']
                for category_action_id, title, url, tab in zip(request.get('id'),
                                                               request.get('title'),
                                                               request.get('url'),
                                                               tabs):
                    category_id, action_id = category_action_id.split('|')
                    row = {}
                    row['title'] = title or tab.get('title')
                    row['url'] = url or tab.get('url')
                    self.saveRequest[category_action_id] = row
        # User pressed the Add button
        elif request.get('form.submit.add'):
            row = {}
            row['title'] = request.get('title')
            row['url'] = request.get('url')
            row['id'] = request.get('id')
            self.addRequest = row


