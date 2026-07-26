# tests/test_full_system.py

import unittest

from core.system_initializer import startup
from core.health_monitor import system_health
from core.performance_tracker import get_statistics
from core.version import version_string
from core.config_validator import validate_config
from core.exchange_monitor import exchange_status





class TestFullSystem(unittest.TestCase):

    def test_startup(self):

        self.assertTrue(
            startup()
        )



    def test_config(self):

        self.assertTrue(
            validate_config()
        )



    def test_health(self):

        health = system_health()

        self.assertTrue(
            health["database"]
        )



    def test_exchange(self):

        status = exchange_status()

        self.assertIn(
            "connected",
            status
        )



    def test_statistics(self):

        stats = get_statistics()

        self.assertIn(
            "profit",
            stats
        )



    def test_version(self):

        self.assertTrue(
            version_string()
        )





if __name__ == "__main__":

    unittest.main()
