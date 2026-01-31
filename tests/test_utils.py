import unittest

from toloka2python import utils


class TestUtils(unittest.TestCase):
    def test_convert_to_bytes_handles_units(self):
        self.assertEqual(utils.convert_to_bytes("1KB"), 1024)
        self.assertEqual(utils.convert_to_bytes("1.5MB"), int(1.5 * 1024**2))
        self.assertEqual(utils.convert_to_bytes("2GB"), 2 * 1024**3)

    def test_convert_to_bytes_unknown_unit_returns_zero(self):
        self.assertEqual(utils.convert_to_bytes("10PB"), 0)

    def test_extract_floats_parses_values(self):
        values = utils.extract_floats("UL/DL rating 1.5 2.0x")
        self.assertEqual(values, [1.5, 2.0])


if __name__ == "__main__":
    unittest.main()
