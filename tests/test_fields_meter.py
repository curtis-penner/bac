import unittest
import logging

import fields.meter
import utils.cmdline
import utils.log


class TestDefaults(unittest.TestCase):
    def test_constructor(self):
        log_obj = utils.log.Log()
        met = fields.meter.Meter(log_obj)
        self.assertIsInstance(met.log, logging.Logger)

class TestParseMeterToken(unittest.TestCase):
    def test_0(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
