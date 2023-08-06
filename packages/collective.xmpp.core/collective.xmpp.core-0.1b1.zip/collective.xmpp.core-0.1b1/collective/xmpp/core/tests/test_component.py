import unittest2 as unittest

from twisted.words.protocols.jabber.jid import JID

from collective.xmpp.core.component import XMPPComponent
from collective.xmpp.core.testing import REACTOR_INTEGRATION_TESTING
from collective.xmpp.core.testing import wait_for_client_state


class ComponentNetworkTest(unittest.TestCase):

    layer = REACTOR_INTEGRATION_TESTING
    level = 2

    def test_component_connection(self):

        component = XMPPComponent('localhost',
                                  5347,
                                  'example.localhost',
                                  'secret')
        self.assertTrue(wait_for_client_state(component, 'authenticated'))
        self.assertEqual(component.jid, JID('example.localhost'))