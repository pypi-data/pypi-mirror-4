from infi import unittest

class ScsiIdTestCase(unittest.TestCase):
    def test_sg0(self):
        from .. import sg_scsi_id as ioctl
        result = ioctl("/dev/sg0")

    def test_sda(self):
        from .. import scsi_ioctl_get_idlun as ioctl
        result = ioctl("/dev/sda")

