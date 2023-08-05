## Controller Python Script "object_paste"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Paste objects into the parent/this folder

from AccessControl import Unauthorized
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import transaction_note
from ZODB.POSException import ConflictError

if not context.cb_dataValid():
    msg = _(u'Copy or cut one or more items to paste.')
    context.plone_utils.addPortalMessage(msg, 'error')
    return state.set(status='failure')

ok = True

try:
    context.manage_pasteObjects(context.REQUEST['__cp'])
except ConflictError:
    raise
except Unauthorized:
    # avoid this unfriendly exception text:
    # "You are not allowed to access 'manage_pasteObjects' in this context"
    msg = _(u'You are not authorized to paste here.')
    ok = False
except Exception as e:
    msg = e
    ok = False

if ok:
    transaction_note('Pasted content to %s' % (context.absolute_url()))
    context.plone_utils.addPortalMessage(_(u'Item(s) pasted.'))
    return state.set(status='success')
else:
    context.plone_utils.addPortalMessage(msg, 'error')
    return state.set(status='failure')
