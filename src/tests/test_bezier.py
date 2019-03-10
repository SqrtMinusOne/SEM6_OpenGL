import unittest

from bezier import ControlElement


class ControlTest(unittest.TestCase):
    def test_has_point(self):
        obj = ControlElement(0.5, 0.5)
        obj.p = 0.2
        self.assertTrue(obj.has_point(0.5, 0.5))
        self.assertTrue(obj.has_point(0.4, 0.5))
        self.assertTrue(obj.has_point(0.4, 0.4))
        self.assertFalse(obj.has_point(0.3, 0.5))
        self.assertFalse(obj.has_point(0.5, 0.7))
