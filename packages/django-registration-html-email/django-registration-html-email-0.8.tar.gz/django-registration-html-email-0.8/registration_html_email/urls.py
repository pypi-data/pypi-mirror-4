"""
Backwards-compatible URLconf for existing django-registration
installs; this allows the standard ``include('registration_html_email.urls')`` to
continue working, but that usage is deprecated and will be removed for
django-registration 1.0. For new installs, use
``include('registration_html_email.backends.default.urls')``.

"""

import warnings

warnings.warn("include('registration_html_email.urls') is deprecated; use include('registration_html_email.backends.default.urls') instead.",
              PendingDeprecationWarning)

from registration_html_email.backends.default.urls import *
