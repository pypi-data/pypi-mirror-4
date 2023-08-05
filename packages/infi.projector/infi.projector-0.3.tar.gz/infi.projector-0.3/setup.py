
SETUP_INFO = dict(
    name = 'infi.projector',
    version = '0.3',
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

    install_requires = ['zc.buildout>=1.6.3', 'infi.execute', 'distribute', 'infi.traceback', 'infi.recipe.template.version>0.4.5', 'gitdb', 'infi.exceptools', 'gitflow', 'smmap', 'infi.pyutils', 'async', 'git-py', 'docopt'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': ['buildout.cfg', '.gitignore', 'README.md', 'bootstrap.py', 'setup.in']},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['projector = infi.projector.scripts:projector'],
        gui_scripts = [],
        projector_command_plugins = ['repository = infi.projector.plugins.builtins.repository:RepositoryPlugin', 'envenv = infi.projector.plugins.builtins.devenv:DevEnvPlugin', 'version = infi.projector.plugins.builtins.version:VersionPlugin', 'requirements = infi.projector.plugins.builtins.requirements:RequirementsPlugin', 'consle_scripts = infi.projector.plugins.builtins.console_scripts:ConsoleScriptsPlugin', 'package_scripts = infi.projector.plugins.builtins.package_scripts:PackageScriptsPlugin', 'package_data = infi.projector.plugins.builtins.package_data:PackageDataPlugin', 'isolated_pyton = infi.projector.plugins.builtins.isolated_python:IsolatedPythonPlugin', 'submodules = infi.projector.plugins.builtins.submodules:SubmodulePlugin']),
    )

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

