from plonetheme.unam.testing import THEMING_INTEGRATION_TESTING

import unittest2 as unittest


class TestIntegration(unittest.TestCase):

    layer = THEMING_INTEGRATION_TESTING

    def test_availableTheme(self):
        from plone.app.theming.utils import getTheme

        theme = getTheme('plonetheme.unam')
        self.assertTrue(theme is not None)
        self.assertEqual(theme.__name__, 'plonetheme.unam')
        self.assertEqual(theme.title, 'Theme UNAM')
