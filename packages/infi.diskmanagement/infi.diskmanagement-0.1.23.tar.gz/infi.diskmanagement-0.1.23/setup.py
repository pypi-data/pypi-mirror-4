
SETUP_INFO = dict(
    name = 'infi.diskmanagement',
    version = '0.1.23',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'https://github.com/Infinidat/infi.diskmanagement',
    license = 'PSF',
    description = """Windows Disk Management wrapping in Python""",
    long_description = """This module gives the same functionality as diskpart. But unlike diskpart, it does not use VDS, it uses SetupAPI and direct IOCTLs to the disks, volumes, and the mount and partitions managers""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['infi.crap', 'capacity', 'infi.wmi', 'distribute', 'infi.instruct', 'waiting', 'infi.pyutils', 'infi.wioctl', 'infi.devicemanager'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = [],
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

