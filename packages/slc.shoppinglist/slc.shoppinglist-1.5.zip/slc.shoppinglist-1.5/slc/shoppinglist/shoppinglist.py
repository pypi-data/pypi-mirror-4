from zope.formlib import form
from five.formlib import formbase
from zope.interface import implements
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IReferenceable

from slc.shoppinglist.interfaces import IShoppinglist
from slc.shoppinglist.widget import ShoppinglistWidget


class ShoppinglistEditForm(formbase.PageForm):
    """ Form for editing the shoppinglist
    """
    form_fields = form.FormFields(IShoppinglist)
    form_fields['uids'].custom_widget = ShoppinglistWidget
    label = u'Edit shopping list'

    def __call__(self):
        self.request.set('disable_border', True)
        return super(ShoppinglistEditForm, self).__call__()

    @form.action(u'Remove')
    def action_remove(self, action, data):
        uids = self.request.get('form.uids')
        if not isinstance(uids, list):
            uids = [uids]
        cnt = self.request.get('form.uids.count')
        remove_uids = list()
        for i in range(int(cnt)):
            val = self.request.get('form.uids.%s' % str(i), None)
            if val:
                remove_uids.append(val)
        new_uids = [x for x in uids if x not in remove_uids]

        self._setUids(new_uids)

    @form.action(u'Clear')
    def action_clear(self, action, data):
        if self.request.get('form.clearList'):
            self._setUids(list())

    def _setUids(self, uids):
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        member.setProperties(shoppinglist=tuple(uids))
        member.ZCacheable_invalidate()


class AddToShoppinglist(BrowserView):
    implements(IShoppinglist)

    def __call__(self):
        context = self.context
        if IReferenceable.providedBy(context):
            uid = context.UID()
            mtool = getToolByName(context, 'portal_membership')
            member = mtool.getAuthenticatedMember()
            if member.hasProperty('shoppinglist'):
                sl = member.getProperty('shoppinglist')
                sl = set(sl)
                sl.add(uid)
                member.setProperties(shoppinglist=tuple(sl))
                member.ZCacheable_invalidate()
                message = u'"%s" added to shoppinglist' \
                    % unicode(context.title_or_id(), 'utf-8')
            else:
                message = u'Member "%s" does not have a shopppinglist in '\
                    'their profile' % unicode(member.getUserName(), 'utf-8')
        else:
            message = u'"%s" could not be added to the shoppinglist, because' \
                'it is not referenceable' % \
                unicode(context.title_or_id(), 'utf-8')

        path = context.absolute_url()
        getToolByName(context, 'plone_utils').addPortalMessage(message)
        self.request.RESPONSE.redirect(path)
