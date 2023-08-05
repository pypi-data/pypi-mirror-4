
SETUP_INFO = dict(
    name = 'infi.recipe.console_scripts',
    version = '0.2.2',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'http://www.infinidat.com',
    license = 'PSF',
    description = """short description here""",
    long_description = """long description here""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['infi.pyutils', 'distribute', 'z3c.recipe.scripts', 'zc.recipe.egg'],
    namespace_packages = ['infi', 'infi.recipe'],

    package_dir = {'': 'src'},
    package_data = {'': ['embed-x86.exe', 'embed-x64.exe', 'Microsoft.VC90.CRT.manifest-x64', 'Microsoft.VC90.CRT.manifest-x86', 'msvcm90.dll-x64', 'msvcm90.dll-x86', 'msvcp90.dll-x64', 'msvcp90.dll-x86', 'msvcr90.dll-x64', 'msvcr90.dll-x86']},
    include_package_data = True,
    zip_safe = False,

    entry_points = {
        'distutils.commands': ['install = infi.recipe.console_scripts:install', ],
        'console_scripts': [],
        'gui_scripts': [],
        'zc.buildout': ['default = infi.recipe.console_scripts:Scripts',
                        'script = infi.recipe.console_scripts:Scripts',
                        'scripts = infi.recipe.console_scripts:Scripts']
        }
    )

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

