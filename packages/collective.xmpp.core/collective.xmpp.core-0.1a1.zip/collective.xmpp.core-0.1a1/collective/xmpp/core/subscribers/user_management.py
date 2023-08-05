import logging
from zope.component import adapter
from zope.component import getUtility
from zope.globalrequest import getRequest

from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.events import \
    IPrincipalCreatedEvent
from Products.PluggableAuthService.interfaces.events import \
    IPrincipalDeletedEvent

from plone.registry.interfaces import IRegistry

from collective.xmpp.core.interfaces import IAdminClient
from collective.xmpp.core.interfaces import IProductLayer
from collective.xmpp.core.interfaces import IXMPPPasswordStorage
from collective.xmpp.core.interfaces import IXMPPUsers
from collective.xmpp.core.utils.users import deletePrincipal
from collective.xmpp.core.utils.users import setupPrincipal

log = logging.getLogger('collective.xmpp.core')

@adapter(IPrincipalCreatedEvent)
def onUserCreation(event):
    """ Create a jabber account for new user.
    """
    request = getRequest()
    if not IProductLayer.providedBy(request):
        return

    client = getUtility(IAdminClient)
    xmpp_users = getUtility(IXMPPUsers)
    principal = event.principal

    principal_id = principal.getUserId()
    principal_jid = xmpp_users.getUserJID(principal_id)
    pass_storage = getUtility(IXMPPPasswordStorage)
    principal_pass = pass_storage.set(principal_id)

    registry = getUtility(IRegistry)
    if registry['collective.xmpp.autoSubscribe']:
        mtool = getToolByName(principal, 'portal_membership')
        members_jids = [xmpp_users.getUserJID(member.getUserId())
                        for member in mtool.listMembers()]
    else:
        members_jids = []

    d = setupPrincipal(client, principal_jid, principal_pass, members_jids)
    return d


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

    d = deletePrincipal(client, principal_jid)
    return d
