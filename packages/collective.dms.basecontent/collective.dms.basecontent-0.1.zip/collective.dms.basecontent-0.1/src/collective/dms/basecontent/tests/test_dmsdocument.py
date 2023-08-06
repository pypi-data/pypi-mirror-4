# -*- coding: utf8 -*-

import unittest2 as unittest

from ecreall.helpers.testing.base import BaseTest

from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from ..dmsdocument import RecipientGroupsVocabulary, TreatingGroupsVocabulary


class TestDmsdocument(unittest.TestCase, BaseTest):
    """Tests adapters"""

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        super(TestDmsdocument, self).setUp()
        self.portal = self.layer['portal']

    def test_RecipientGroupsVocabulary(self):
        voc_inst = RecipientGroupsVocabulary()
        voc_dic = voc_inst(self.portal).by_token
        self.assertEquals(set(voc_dic), set(self.portal.portal_groups.listGroupNames()))

    def test_TreatingGroupsVocabulary(self):
        voc_inst = TreatingGroupsVocabulary()
        voc_dic = voc_inst(self.portal).by_token
        self.assertEquals(set(voc_dic), set(self.portal.portal_groups.listGroupNames()))
