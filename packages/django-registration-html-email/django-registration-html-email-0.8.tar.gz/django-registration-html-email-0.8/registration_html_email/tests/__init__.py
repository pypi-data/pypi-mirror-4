from django.test import TestCase

import registration

from registration_html_email.tests.backends import *
from registration_html_email.tests.forms import *
from registration_html_email.tests.models import *
from registration_html_email.tests.views import *


class RegistrationVersionInfoTests(TestCase):
    """
    Test django-registration's internal version-reporting
    infrastructure.
    
    """
    def setUp(self):
        self.version = registration_html_email.VERSION

    def tearDown(self):
        registration_html_email.VERSION = self.version
    
    def test_get_version(self):
        """
        Test the version-info reporting.
        
        """
        versions = [
            {'version': (1, 0, 0, 'alpha', 0),
             'expected': "1.0 pre-alpha"},
            {'version': (1, 0, 1, 'alpha', 1),
             'expected': "1.0.1 alpha 1"},
            {'version': (1, 1, 0, 'beta', 2),
             'expected': "1.1 beta 2"},
            {'version': (1, 2, 1, 'rc', 3),
             'expected': "1.2.1 rc 3"},
            {'version': (1, 3, 0, 'final', 0),
             'expected': "1.3"},
            {'version': (1, 4, 1, 'beta', 0),
             'expected': "1.4.1 beta"},
            ]
        
        for version_dict in versions:
            registration_html_email.VERSION = version_dict['version']
            self.assertEqual(registration_html_email.get_version(), version_dict['expected'])
