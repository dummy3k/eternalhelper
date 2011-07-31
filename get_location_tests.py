import unittest
from get_location import Extractor

class LocationExtratorTests(unittest.TestCase):
    def test_welcome(self):
        ex = Extractor()
        self.assertTrue(ex.feed("Welcome to the Desert Pines storage"))
        self.assertEqual("Desert Pines storage", ex.map_name)

    def test_dp_sto(self):
        ex = Extractor()
        self.assertTrue(ex.feed("Welcome to the Desert Pines storage"))
        self.assertTrue(ex.feed("You are in   [98,38]"))
        self.assertEqual("Desert Pines storage", ex.map_name)
        self.assertEqual( (98,38), ex.loc)

    def test_exit_dp_sto(self):
        ex = Extractor()
        self.assertTrue(ex.feed("You are in Desert Pines  [166,100]"))
        self.assertEqual("Desert Pines", ex.map_name)
        self.assertEqual( (166,100), ex.loc)

