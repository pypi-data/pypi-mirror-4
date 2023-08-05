
SETUP_INFO = dict(
    name = 'infi.multipathtools',
    version = '0.1.16',
    author = 'Arnon Yaari',
    author_email = 'arnony@infinidat.com',

    url = 'http://www.infinidat.com',
    license = 'PSF',
    description = """python bindings to multipath-tools daemon""",
    long_description = """python bindings to multipath-tools daemon""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['distribute', 'infi.execute', 'infi.exceptools', 'infi.instruct', 'bunch'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': ['*txt']},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['print_maps = infi.multipathtools.scripts:print_maps', 'print_config = infi.multipathtools.scripts:print_config', 'print_model_examples = infi.multipathtools.model.scripts:print_examples'],
        gui_scripts = []),
    )

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

