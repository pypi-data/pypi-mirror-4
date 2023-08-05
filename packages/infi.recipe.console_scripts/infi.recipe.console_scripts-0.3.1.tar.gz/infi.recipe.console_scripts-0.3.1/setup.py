
SETUP_INFO = dict(
    name = 'infi.recipe.console_scripts',
    version = '0.3.1',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'https://github.com/Infinidat/infi.recipe.console_scripts',
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

    install_requires = ['infi.pyutils', 'zc.recipe.egg==1.3.2', 'distribute', 'z3c.recipe.scripts', 'mock'],
    namespace_packages = ['infi', 'infi.recipe'],

    package_dir = {'': 'src'},
    package_data = {'': ['msvcp90.dll-x86', 'embed-x86.exe', 'embed-gui-x86.exe', 'msvcp90.dll-x64', 'embed-gui-x64.exe', 'embed-x64.exe', 'msvcr90.dll-x86', 'Microsoft.VC90.CRT.manifest-x86', 'msvcm90.dll-x64', 'msvcm90.dll-x86', 'Microsoft.VC90.CRT.manifest-x64', 'msvcr90.dll-x64']},
    include_package_data = True,
    zip_safe = False,

    entry_points = {
        'console_scripts': [],
        'gui_scripts': ['gui-script-test = infi.recipe.console_scripts:nothing'],
        'zc.buildout': ['default = infi.recipe.console_scripts:Scripts',
                        'script = infi.recipe.console_scripts:Scripts',
                        'scripts = infi.recipe.console_scripts:Scripts',
                        'gui_script = infi.recipe.console_scripts:GuiScripts',
                        'gui_scripts = infi.recipe.console_scripts:GuiScripts',]
        }
    )

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

