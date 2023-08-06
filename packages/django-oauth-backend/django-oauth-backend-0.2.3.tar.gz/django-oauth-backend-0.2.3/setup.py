# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from setuptools import setup

from oauth_backend import __version__


setup(
    name = "django-oauth-backend",
    version = __version__,
    author = "Canonical ISD Hackers",
    author_email = "canonical-isd@lists.launchpad.net",
    license = "AGPLv3",
    packages = ['oauth_backend', 'oauth_backend.migrations'],
    zip_safe = True,
)
