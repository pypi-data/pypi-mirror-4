__version__ = "0.1.42"
__git_commiter_name__ = "Guy Rozendorn"
__git_commiter_email__ = "guy@rzn.co.il"
__git_branch__ = '(Not currently on any branch)'
__git_remote_tracking_branch__ = '(No remote tracking)'
__git_remote_url__ = '(Not remote tracking)'
__git_head_hash__ = '8d620a51f5b3cf1e3ba07ddd11896a3b6ba33bcc'
__git_head_subject__ = 'Finished release v0.1.42.'
__git_head_message__ = '* release/v0.1.42:\n  TRIVIAL rescan_scsi_sh: no removing lun during lun_scan\n  TRIVIAL rescan_scsi_sh: do nothing if target was removed\n  TRIVIAL rescan_scsi_sh: detailed exceptions when catching IOErrors from sysfs\n  TRIVIAL rscan_scsi_bus: removing call to scsi_host_scan from rescan_scsi_host\n  TRIVIAL rescan_scsi_bus: avoiding /proc/scsi/scsi\n  TRIVIAL rescan_scsi_bus: logging improvement\n  TRIVIAL rescan_scsi_bus: handle_add_devices will use add_single_device iff scsi_host_scan failed\n  TRIVIAL rescan_scsi_bus: fixing scsi_host_scan\n  TRIVIAL rescan_scsi_bus: get_luns_from_report_luns\n  TRIVIAL rescan_scsi_bus: will not attempt to remove from proc if remove from sysfs succeeded\n  TRIVIAL rescan_scsi_bus: always to scsi_host_scan to find new targets\n  TRIVIAL rescan_scsi_bus: existing luns is an intersection between actual and missing, not union\n  TRIVIAL deleting old linux rescan tests\n  TRIVIAL moving readlink imports to inside functions so the import for the module would work on Windows\n  buildout.cfg: adding infi.asi >= 0.3.5 to requirements\n  buildout.cfg: adding infi.asi >= 0.3.4 to requirements\n  STORAGEMODEL-187 LinuxNativeMultipathBlockDevice now uses the new LinuxIoctlCommandExecuter\n  buildout.cfg: adding infi.asi>=0.3.2 to requirements\n  empty commit after version v0.1.41'
__git_dirty_diff__ = ''