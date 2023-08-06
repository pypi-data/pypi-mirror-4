
SETUP_INFO = dict(
    name = 'infi.storagemodel',
    version = '0.1.52',
    author = 'Arnon Yaari',
    author_email = 'arnony@infinidat.com',

    url = 'https://github.com/Infinidat/infi.storagemodel',
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

    install_requires = ['infi.dtypes.hctl', 'infi.devicemanager', 'infi.traceback', 'infi.parted', 'infi.multipathtools', 'distribute', 'infi.instruct', 'infi.diskmanagement', 'infi.hbaapi', 'infi.cwrap', 'infi.mountoolinux', 'daemon', 'infi.dtypes.wwn', 'infi.sgutils', 'infi.exceptools', 'infi.wmpio', 'infi.asi', 'infi.pyutils', 'infi.wioctl', 'Brownie'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['devlist = infi.storagemodel.examples:devlist', 'rescan_scsi_bus = infi.storagemodel.linux.rescan_scsi_bus:console_script'],
        gui_scripts = [],
        ),
)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

