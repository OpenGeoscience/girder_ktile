#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tests import base
from girder.models.model_base import ValidationException


# For more on testing your Python plugins, see:
# http://girder.readthedocs.io/en/latest/plugin-development.html#automated-testing-for-plugins
def setUpModule():
    base.enabledPlugins.append('girder_ktile')
    base.startServer()


def tearDownModule():
    base.stopServer()


class kTileTest(base.TestCase):
    def setUp(self):
        super(kTileTest, self).setUp()

        self.admin_user = self.model('user').createUser('test', 'testpass', 'test',
                                                        'test', 'test@test.test', admin=True)

    def testItemMetadataGetsAdded(self):
        pass
        # item = self.model('item').createItem('test item', self.admin_user, )
        # self.assert

    def testItemMetadataFailureGetsLogged(self):
        pass

    def testItemMetadataValidates(self):
        from girder.plugins.girder_ktile.constants import PluginSettings

        with self.assertRaises(ValidationException):
            self.model('setting').set(PluginSettings.ITEM_METADATA, '')

    def testItemMetadataRetrieval(self):
        from girder.plugins.girder_ktile.constants import PluginSettings

        # Test default value is retrieved
        resp = self.request('/ktile/item_metadata', user=self.admin_user)
        self.assertStatusOk(resp)
        self.assertEqual(resp.json, 'default_value')

        # Change the value and test the new value is retrieved
        self.model('setting').set(PluginSettings.ITEM_METADATA, 'new_value')
        resp = self.request('/ktile/item_metadata', user=self.admin_user)
        self.assertStatusOk(resp)
        self.assertEqual(resp.json, 'new_value')
