from Products.Five.browser import BrowserView
from zope.component import getUtility, getMultiAdapter,queryMultiAdapter
from Products.CMFCore.utils import getToolByName
from simplelayout.base.utils import IBlockControl
from z3c.json import minjson as json
from Products.CMFPlone.utils import isLinked
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _pl_
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class ChangeLayout(BrowserView):

    template = ViewPageTemplateFile('content.pt')

    def __call__(self, uid=None, layout="", viewname="block_view"):
        rc = getToolByName(self.context, 'reference_catalog')
        if uid and layout:
            uid = uid.replace('uid_','')
            block = rc.lookupObject(uid)
            converter = getUtility(IBlockControl, name='block-layout')
            converter.update(self.context, block, self.request, layout=layout, viewname=viewname)  
            self.block_view = queryMultiAdapter((block, self.request), name='block_view-%s' % viewname)
            #fallback
            if self.block_view is None:
                self.block_view = queryMultiAdapter((block, self.request), name='block_view')
            return self.template()
        

class DeletePopup(BrowserView):
    template = ViewPageTemplateFile("delete_confirmation.pt")
    locked_template = ViewPageTemplateFile("locked_information.pt")

    info = None
    lock_is_stealable = None
    lock_info = None
    

    def __call__(self):

        context = self.context
        request = context.REQUEST
        
        # copied from delete_confirmation controller script    
        if isLinked(context):

            parent = context.aq_inner.aq_parent
            title = safe_unicode(context.title_or_id())

            try:
                lock_info = context.restrictedTraverse('@@plone_lock_info')
            except AttributeError:
                lock_info = None
            
            if lock_info is not None and lock_info.is_locked():
                message = _pl_(u'${title} is locked and cannot be deleted.',
                    mapping={u'title' : title})
            else:
                parent.manage_delObjects(context.getId())
                message = _pl_(u'${title} has been deleted.',
                            mapping={u'title' : title})
                transaction_note('Deleted %s' % context.absolute_url())

            context.plone_utils.addPortalMessage(message)
            return context.REQUEST.RESPONSE.redirect(object.aq_inner.aq_parent.absolute_url())
        else:

            #check for lock info
            try:            
                lock_info = context.restrictedTraverse('@@plone_lock_info')
            except AttributeError:
                lock_info = None
                
            if lock_info is not None and lock_info.is_locked():
                lock_view = getMultiAdapter((context, request), name="plone_lock_info")
                self.info = lock_view
                self.lock_is_stealable = self.info.lock_is_stealable()
                self.lock_info = self.info.lock_info()
                return self.locked_template()
                
            return self.template()


class DeleteObject(BrowserView):
    def __call__(self):
        context = self.context
        
        try:
            context.manage_delObjects([context.id])
            return "done"
        except:
            return ""
        return ""
        
class RenderBlockControls(BrowserView):
    def __call__(self, uids):
        rc = getToolByName(self.context, 'reference_catalog')
        uids = uids.split(',')
        result = {}
        result['container'] = self.context.restrictedTraverse("@@sl_controls")()
        result['items'] = []
        for key in uids:
            if not key:
                continue
            uid = key.split('_')[1]
            object_ = rc.lookupObject(uid)
            if object_ is not None:
                controls = object_.restrictedTraverse("@@sl_controls")
                result['items'].append(dict(id=key,data=controls()))
        return json.write(result)
