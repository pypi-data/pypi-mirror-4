# -*- coding: utf-8 -*-
import unittest
from fabricator.config import fill_fabric_env
from fabric.state import env


class ConfigTestCase(unittest.TestCase):
    def test_get_config(self):
        fill_fabric_env(env, 'test_project.test_config', 'test_config')