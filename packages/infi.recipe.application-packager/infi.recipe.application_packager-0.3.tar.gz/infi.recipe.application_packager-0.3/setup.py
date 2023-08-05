
SETUP_INFO = dict(
    name = 'infi.recipe.application_packager',
    version = '0.3',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'http://www.infinidat.com',
    license = 'PSF',
    description = """buildout recipe for packaging projects as applications""",
    long_description = """buildout recipe for packaging projects are applications""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['infi.execute', 'lxml', 'infi.registry', 'distribute', 'infi.pypi_manager', 'Archive', 'infi.pyutils', 'git-py', 'infi.projector'],
    namespace_packages = ['infi', 'infi.recipe'],

    package_dir = {'': 'src'},
    package_data = {'': ['postinst.in', 'signtool.exe', 'control.in', 'changelog.in', 'rules.in', 'prerm.in', 'template.wxs', 'silent_launcher-x86.exe', 'rpmspec.in', 'md5sums.in', 'silent_launcher-x64.exe']},
    include_package_data = True,
    zip_safe = False,

    entry_points = {
        'console_scripts': ['pre_uninstall = infi.recipe.application_packager.scripts:pre_uninstall', 'hello = infi.recipe.application_packager.scripts:main', 'post_install = infi.recipe.application_packager.scripts:post_install', 'sample = infi.recipe.application_packager.scripts:sample'],
        'gui_scripts': [],
        'zc.buildout': [
                        'default = infi.recipe.application_packager.auto:Recipe',
                        'msi = infi.recipe.application_packager.msi:Recipe',
                        'rpm = infi.recipe.application_packager.rpm:Recipe',
                        'deb = infi.recipe.application_packager.deb:Recipe',
                       ]
        },
    )

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

