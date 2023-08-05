from infi.dtypes.hctl import HCTL

def get_hctl_for_sg_device(device_path):
    from ..ioctl import sg_scsi_id as _ioctl
    struct = _ioctl(device_path)
    return HCTL(struct.host_no, struct.channel, struct.scsi_id, struct.lun)

def get_hctl_for_sd_device(device_path):
    from ..ioctl import scsi_ioctl_get_idlun as _ioctl
    struct = _ioctl(device_path)
    # http://tldp.org/HOWTO/SCSI-Generic-HOWTO/scsi_g_idlun.html
    # "four_in_one" is made up as follows:
    # (scsi_device_id | (lun << 8) | (channel << 16) | (host_no << 24))
    host = (struct.four_in_one >> 24)
    channel = (struct.four_in_one >> 16) & 0xFF
    target = (struct.four_in_one) & 0xFF
    lun = (struct.four_in_one >> 8) & 0xFF
    result = HCTL(host, channel, target, lun)
    return HCTL(host, channel, target, lun)

def get_sg_to_hctl_mappings():
    from glob import glob
    return {device_path:get_hctl_for_sg_device(device_path) for device_path in glob("/dev/sg*")}

def get_sd_to_hctl_mappings():
    from glob import glob
    from os.path import sep
    sd_devices = filter(lambda path: path.split(sep)[-1].isalpha(), glob("/dev/sd*"))
    return {device_path:get_hctl_for_sd_device(device_path) for device_path in sd_devices}

def get_hctl_to_sd_mappings():
    return {hctl:device_path for device_path,hctl in get_sd_to_hctl_mappings().items()}

def get_sd_from_sg(sg):
    hctl = get_hctl_for_sg_device(sg)
    return get_hctl_to_sd_mappings()[hctl]

