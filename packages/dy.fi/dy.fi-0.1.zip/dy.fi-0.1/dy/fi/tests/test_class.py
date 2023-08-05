import unittest


class DyFiTestCase(unittest.TestCase):

    def test_last_update(self):
        from datetime import datetime
        from dy.fi import last_updated
        self.assertIsInstance(last_updated(), datetime)
