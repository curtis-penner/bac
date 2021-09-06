import unittest
import logging

import meter
import log


class TestDefaults(unittest.TestCase):
    def test_constructor(self):
        log_obj = log.Log()
        met = meter.Meter(log_obj)
        self.assertIsInstance(met.log, logging.Logger)

class TestParseMeterToken(unittest.TestCase):
    def test_0(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
