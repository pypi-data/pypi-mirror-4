"Test helper functions and base test cases."
from __future__ import unicode_literals

import random
import string

from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase
try:
    from django.utils.six import StringIO
except ImportError:
    # Django < 1.5. No Python 3 support
    from StringIO import StringIO

from adcode.models import Section, Size, Placement


class AdCodeDataTestCase(TestCase):
    "Base test case for creating adcode models."

    def tearDown(self):
        cache.clear()

    def get_random_string(self, length=10):
        return ''.join(random.choice(string.ascii_letters) for x in range(length))

    def create_section(self, **kwargs):
        "Factory method for creating Sections."
        defaults = {
            'name': self.get_random_string(),
            'slug': self.get_random_string(),
            'pattern': '^/',
        }
        defaults.update(kwargs)
        return Section.objects.create(**defaults)

    def create_size(self, **kwargs):
        "Factory method for creating Sizes."
        defaults = {
            'name': self.get_random_string(),
            'width': random.randint(50, 100),
            'height': random.randint(50, 100),
        }
        defaults.update(kwargs)
        return Size.objects.create(**defaults)

    def create_placement(self, **kwargs):
        "Factory method for creating Placements."
        defaults = {
            'name': self.get_random_string(),
            'slug': self.get_random_string(),
            'remote_id': self.get_random_string(),
        }
        defaults.update(kwargs)
        if 'size' not in defaults:
            defaults['size'] = self.create_size()
        return Placement.objects.create(**defaults)


class FixturesTestCase(TestCase):
    "Ensure that provided fixtures load."

    def test_iab_sizes(self):
        "Load IAB size fixture."
        out = StringIO()
        err = StringIO()
        call_command('loaddata', 'iab_sizes.json', stdout=out, stderr=err)
        self.assertEqual(Size.objects.all().count(), 27)
