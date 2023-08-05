
SETUP_INFO = dict(
    name = 'infi.storagemodel',
    version = '0.1.42',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'http://www.infinidat.com',
    license = 'PSF',
    description = """A high-level library for traversing the OS storage model.""",
    long_description = """A high-level cross-platform abstraction of the OS storage stack (LUNs, disks, volumes, etc).""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['infi.dtypes.hctl', 'infi.asi>=0.3.2', 'distribute', 'infi.pyutils >= 0.0.20', 'Brownie', 'infi.devicemanager >= 0.1.7', 'infi.instruct >= 0.5.9', 'infi.hbaapi >= 0.1.14', 'infi.mountoolinux >= 0.1.5', 'infi.multipathtools >= 0.1.12', 'daemon', 'infi.dtypes.wwn', 'infi.diskmanagement >= 0.1.15', 'infi.exceptools', 'infi.cwrap >= 0.2.3', 'infi.asi >= 0.3.5', 'infi.sgutils >= 0.1', 'infi.parted >= 0.1.4', 'infi.wioctl', 'infi.wmpio >= 0.1.7'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['devlist = infi.storagemodel.examples:devlist', 'rescan_scsi_bus = infi.storagemodel.linux.rescan_scsi_bus:console_script'],
        gui_scripts = []),
    )

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

