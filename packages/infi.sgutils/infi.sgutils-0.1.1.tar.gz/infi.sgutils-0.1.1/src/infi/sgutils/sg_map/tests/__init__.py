from infi import unittest

class SgMapTestCase(unittest.TestCase):

    def test_get_sg_to_hctl_mappings(self):
        from .. import get_sg_to_hctl_mappings as getter
        result = getter()
        self.assertIn("/dev/sg0", result.keys())

    def test_get_sd_to_hctl_mappings(self):
        from .. import get_sd_to_hctl_mappings as getter
        result = getter()
        self.assertIn("/dev/sda", result.keys())

    def test_get_hctl_to_sd_mappings(self):
        from .. import get_hctl_to_sd_mappings as getter
        result = getter()

    def test_sg_to_sd(self):
        from .. import get_sd_from_sg
        self.assertIn(get_sd_from_sg("/dev/sg1"), ["/dev/sda", "/dev/sdb"])

