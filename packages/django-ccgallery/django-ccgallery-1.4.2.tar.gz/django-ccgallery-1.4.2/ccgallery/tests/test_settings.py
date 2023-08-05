from django.test import TestCase
from django.conf import settings
from ccgallery import settings as c_settings
from ccgallery.models import get_model


class FakeModel(object):
    """Does nothing. Used in the testcases"""


class SettingTestCases(TestCase):

    def setUp(self):
        reload(c_settings)

    def tearDown(self):
        try:
            del(settings.CCGALLERY_MODEL)
        except AttributeError:
            pass

    def test_nonsense_model(self):
        """ if a custom model doesn't exists we get the
        bundled model returned"""
        # set thesettings.CCCONTACT_MODEL custom model
        settings.CCGALLERY_MODEL = 'nonsense.JabberWocky'
        reload(c_settings)
        self.assertEqual(
                get_model()._meta.module_name,
                'item')
        self.assertEqual(
                get_model()._meta.app_label,
                'ccgallery')

    def test_default_model(self):
        """The cccontact.model.Contact models is the default model"""
        self.assertEqual(
                get_model()._meta.module_name,
                'item')
        self.assertEqual(
                get_model()._meta.app_label,
                'ccgallery')

    def test_custom_model(self):
        """The custom model can be overridden"""
        # set thesettings.CCCONTACT_MODEL custom model
        settings.CCGALLERY_MODEL = 'ccgallery.tests.test_settings.FakeModel'
        reload(c_settings)
        # we have the fake model
        self.assertEqual('FakeModel', get_model().__name__)
