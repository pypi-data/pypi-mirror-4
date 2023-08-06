"""some utilities for testing forge security

:organization: Logilab
:copyright: 2008-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubes.tracker.testutils import SecurityTC

class ForgeSecurityTC(SecurityTC):

    def setUp(self):
        SecurityTC.setUp(self)
        # implicitly test manager can add some entities
        req = self.request()
        req.create_entity('License', name=u'license')
        self.extproject = req.create_entity('ExtProject', name=u'projet externe')
        self.commit()
