#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_moma-django
----------------------------------

Tests for `moma-django` module.
"""

import os
import sys
import unittest


#set path
TEST_ROOT = os.path.dirname(__file__)
PROJECT_ROOT = os.path.join(TEST_ROOT, '..')
MOMA_EXAMPLE_ROOT = os.path.join(PROJECT_ROOT, 'moma_example')

sys.path.append(PROJECT_ROOT)
sys.path.append(MOMA_EXAMPLE_ROOT) #we are using settings.py from the example

sys.path.insert(0, MOMA_EXAMPLE_ROOT)

#Ensure Django is configured to use our example site
os.environ['DJANGO_SETTINGS_MODULE'] = 'moma_example.settings'


#run the tests

from django.core.management import execute_from_command_line
execute_from_command_line([MOMA_EXAMPLE_ROOT+'/manage.py', 'test', 'testing'])
