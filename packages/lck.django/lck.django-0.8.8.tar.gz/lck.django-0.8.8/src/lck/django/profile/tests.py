#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 by Łukasz Langa
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Test for common routines and models."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf import settings
from django.test import TestCase
from django.utils.unittest import skipUnless


@skipUnless("lck.dummy.defaults" in settings.INSTALLED_APPS,
            "Requires the lck.dummy.defaults to be installed.")
class TestModels(TestCase):
    def test_creation(self):
        from django.contrib.auth.models import User
        from lck.dummy.defaults.models import Profile

        u = User(username='pinky', email='pinky@brain.com',
                 first_name='Pinky', last_name='Mouse')
        with self.assertRaises(Profile.DoesNotExist):
            u.get_profile()
        u.save()
        self.assertEqual(u.username, u.get_profile().nick)

    def test_profile_attribute_passing(self):
        self.test_creation()
        from lck.dummy.defaults.models import Profile
        p = Profile.objects.all()[0]
        with self.assertNumQueries(1):
            self.assertEqual(p.nick, 'pinky')
            self.assertEqual(p.email, 'pinky@brain.com')
            self.assertEqual(p.get_full_name(), 'Pinky Mouse')
            self.assertFalse(p.is_anonymous())
