import logging
from zope.component import adapter
from zope.component import getUtility
from zope.globalrequest import getRequest
from Products.PluggableAuthService.interfaces.events import IPrincipalDeletedEvent
from collective.xmpp.core.interfaces import IAdminClient
from collective.xmpp.core.interfaces import IProductLayer
from collective.xmpp.core.interfaces import IXMPPPasswordStorage
from collective.xmpp.core.interfaces import IXMPPUsers
from collective.xmpp.core.utils import users

log = logging.getLogger(__name__)


@adapter(IPrincipalDeletedEvent)
def onUserDeletion(event):
    """ Delete jabber account when a user is removed.
    """
    request = getRequest()
    if not IProductLayer.providedBy(request):
        return

    client = getUtility(IAdminClient)
    xmpp_users = getUtility(IXMPPUsers)

    principal_id = event.principal
    principal_jid = xmpp_users.getUserJID(principal_id)

    pass_storage = getUtility(IXMPPPasswordStorage)
    pass_storage.remove(principal_id)

    d = users.deletePrincipal(client, principal_jid)
    return d



