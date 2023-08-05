
SETUP_INFO = dict(
    name = 'infi.projector',
    version = '0.5.5',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'https://github.com/Infinidat/infi.projector',
    license = 'PSF',
    description = """Python, git-flow based project management tool""",
    long_description = """For the complete document, see the README.md file over at GitHub""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['zc.buildout>=1.6.3', 'gitdb>=0.5.4', 'git-py>=1.0.0', 'docopt>=0.5.0', 'infi.recipe.template.version>=0.4.10', 'gitflow>=0.5.0', 'async>=0.6.1', 'distribute>=0.6.32', 'infi.execute>=0.0.8', 'infi.exceptools>=0.2.2', 'infi.pyutils>=0.0.27', 'smmap>=0.8.2', 'infi.traceback>=0.3.3'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': ['buildout.cfg', '.gitignore', 'README.md', 'bootstrap.py', 'setup.in']},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['projector = infi.projector.scripts:projector'],
        gui_scripts = [],
        projector_command_plugins = ['repository = infi.projector.plugins.builtins.repository:RepositoryPlugin', 'envenv = infi.projector.plugins.builtins.devenv:DevEnvPlugin', 'version = infi.projector.plugins.builtins.version:VersionPlugin', 'requirements = infi.projector.plugins.builtins.requirements:RequirementsPlugin', 'console_scripts = infi.projector.plugins.builtins.console_scripts:ConsoleScriptsPlugin', 'gui_scripts = infi.projector.plugins.builtins.gui_scripts:GuiScriptsPlugin', 'package_scripts = infi.projector.plugins.builtins.package_scripts:PackageScriptsPlugin', 'package_data = infi.projector.plugins.builtins.package_data:PackageDataPlugin', 'isolated_pyton = infi.projector.plugins.builtins.isolated_python:IsolatedPythonPlugin', 'submodules = infi.projector.plugins.builtins.submodules:SubmodulePlugin']),
    )

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

