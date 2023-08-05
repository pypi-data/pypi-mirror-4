
from contextlib import contextmanager
from logging import getLogger
logger = getLogger(__name__)

BUILDOUT_PARAMETERS = ['-s']

class PrettyExecutionError(Exception):
    # infi.execute.ExecutionError does print stdout and stderr well, and this is a must when running buildout
    def __init__(self, result):
        super(PrettyExecutionError, self).__init__("Execution of %r failed!\nresult=%s\nstdout=%s\nstderr=%s" % (result._command,
                                                                                                                 result.get_returncode(),
                                                                                                                 result.get_stdout(),
                                                                                                                 result.get_stderr()))
        self.result = result

def _chdir_and_log(path):
    from os import chdir
    chdir(path)
    logger.debug("Changed directory to {!r}".format(path))

@contextmanager
def chdir(path):
    from os.path import abspath
    from os import curdir
    path = abspath(path)
    current_dir = abspath(curdir)
    _chdir_and_log(path)
    try:
        yield
    finally:
        _chdir_and_log(current_dir)

@contextmanager
def open_buildout_configfile(filepath="buildout.cfg", write_on_exit=False):
    from ConfigParser import ConfigParser
    parser = ConfigParser()
    parser.read(filepath)
    try:
        yield parser
    finally:
        if not write_on_exit:
            return
        with open(filepath, 'w') as fd:
            parser.write(fd)

def is_running_inside_virtualenv():
    import sys
    return hasattr(sys, 'real_prefix')

def parse_args(commandline_or_args):
    return commandline_or_args if isinstance(commandline_or_args, list) else commandline_or_args.split()

def execute_assert_success(args):
    from infi import execute
    logger.info("Executing {}".format(' '.join(args)))
    result = execute.execute(args)
    if result.get_returncode() is not None and result.get_returncode() != 0:
        raise PrettyExecutionError(result)

def _get_executable_from_shebang_line():  # pragma: no cover
    # The executable wrapper in distribute dynamically loads Python's DLL, which causes sys.executable to be the wrapper
    # and not the original python exeuctable. We have to find the real executable as Distribute does.
    from os import path
    import sys
    executable_script_py = sys.executable.replace(".exe", "-script.py")
    if not path.exists(executable_script_py):
        # using original Python executable
        return sys.executable
    with open(executable_script_py) as fd:
        shebang_line = fd.readlines()[0].strip()
    executable_path = path.normpath(shebang_line[2:])
    return (executable_path + '.exe') if not executable_path.endswith('.exe') else executable_path

def execute_with_python(commandline_or_args):
    import sys
    from ..assertions import is_windows
    args = parse_args(commandline_or_args)
    executable = [sys.executable if not is_windows() else _get_executable_from_shebang_line()]
    if not is_running_inside_virtualenv():
        executable.append('-S')
    try:
        execute_assert_success(executable + args)
    except PrettyExecutionError:
        logger.warning("Command falied with -S, trying without")
        executable.remove('-S')
        execute_assert_success(executable + args)

def execute_with_isolated_python(commandline_or_args):
    import sys
    import os
    from ..assertions import is_windows
    args = parse_args(commandline_or_args)
    executable = [os.path.join('parts', 'python', 'bin', 'python{}'.format('.exe' if is_windows() else ''))]
    with open_buildout_configfile() as buildout:
        if buildout.get('buildout', 'relative-paths') in ['True', 'true']:
            [executable] = os.path.abspath(executable[0])
    execute_assert_success(executable + args)

def execute_with_buildout(commandline_or_args):
    from os import name, path
    args = parse_args(commandline_or_args)
    execute_assert_success([path.join('bin', 'buildout{}'.format('.exe' if name == 'nt' else ''))] + \
                            BUILDOUT_PARAMETERS + args)

@contextmanager
def buildout_parameters_context(parameters):
    try:
        _ = [BUILDOUT_PARAMETERS.append(param) for param in parameters if param not in BUILDOUT_PARAMETERS]
        yield
    finally:
        _ = [BUILDOUT_PARAMETERS.remove(param) for param in parameters if param in BUILDOUT_PARAMETERS]

def _release_version_with_git_flow(version_tag):
    from os import curdir
    from gitflow.core import GitFlow
    from gitpy import LocalRepository
    gitflow = GitFlow()
    gitflow.create("release", version_tag, base=None, fetch=False)
    gitflow.finish("release", version_tag, fetch=False, rebase=False, keep=False, force_delete=True,
                   tagging_info=dict(sign=False, message=version_tag))
    repository = LocalRepository(curdir)
    repository.checkout("develop")
    repository.commit("empty commit after version {}".format(version_tag), allowEmpty=True)
    repository.createTag("{}-develop".format(version_tag))

def git_checkout(branch_name_or_tag):
    from os import curdir
    from gitpy import LocalRepository
    try:
        LocalRepository(curdir).checkout(branch_name_or_tag)
    except Exception: # pragma: no cover
        logger.error("failed to checkout {}".format(branch_name_or_tag))
        raise SystemExit(1)

def commit_changes_to_buildout(message):
    from os import curdir
    from gitpy import LocalRepository
    repository = LocalRepository(curdir)
    if "buildout.cfg" not in [modified_file.filename for modified_file in repository.getChangedFiles()]:
        return
    repository.add("buildout.cfg")
    repository.commit("buildout.cfg: " + message)

def get_latest_version():
    from os import curdir
    from gitpy import LocalRepository
    from pkg_resources import parse_version
    repository = LocalRepository(curdir)
    version_tags = [tag.name for tag in repository.getTags()
                    if tag.name.startswith('v') and not tag.name.endswith('-develop')]
    version_tags.sort(key=lambda ver: parse_version(ver))
    return version_tags[-1]

@contextmanager
def open_tempfile():
    from tempfile import mkstemp
    from os import close, remove
    fd, path = mkstemp()
    close(fd)
    try:
        yield path
    finally:
        try:
            remove(path)
        except:
            pass

def set_freezed_versions_in_install_requires(buildout_cfg, versions_cfg):
    from .package_sets import InstallRequiresPackageSet, VersionSectionSet, from_dict, to_dict
    install_requires = to_dict(InstallRequiresPackageSet.from_value(buildout_cfg.get("project", "install_requires")))
    versions = to_dict(VersionSectionSet.from_value(versions_cfg))
    for key, value in versions.items():
        if install_requires.has_key(key):
            install_requires[key] = value
    install_requires = from_dict(install_requires)
    install_requires = set([item.replace('==', ">=") for item in install_requires])
    buildout_cfg.set("project", "install_requires", InstallRequiresPackageSet.to_value(install_requires))

def freeze_versions(versions_file, change_install_requires):
    from os import curdir, path
    with open_buildout_configfile(write_on_exit=True) as buildout_cfg:
        buildout_cfg.set("buildout", "extensions",  "buildout-versions")
        buildout_cfg.set("buildout", "versions", "versions")
        with open_buildout_configfile(versions_file) as versions_cfg:
            if not buildout_cfg.has_section("versions"):
                buildout_cfg.add_section("versions")
            for option in buildout_cfg.options("versions"):
                buildout_cfg.remove_option("versions", option)
            for option in versions_cfg.options("versions"):
                buildout_cfg.set("versions", option, versions_cfg.get("versions", option))
        if change_install_requires:
                set_freezed_versions_in_install_requires(buildout_cfg, versions_cfg)

def unset_freezed_versions_in_install_requires(buildout_cfg):
    from .package_sets import InstallRequiresPackageSet, to_dict, from_dict
    install_requires = InstallRequiresPackageSet.from_value(buildout_cfg.get("project", "install_requires"))
    install_requires_dict = to_dict(install_requires)
    install_requires_dict.update({key:[] for key, specs in install_requires_dict.items()
                                  if specs and specs[-1][0] == '>='})
    install_requires = from_dict(install_requires_dict)
    buildout_cfg.set("project", "install_requires", InstallRequiresPackageSet.to_value(install_requires))

def unfreeze_versions(change_install_requires):
    with open_buildout_configfile(write_on_exit=True) as buildout_cfg:
        buildout_cfg.remove_option("buildout", "extensions")
        buildout_cfg.remove_option("buildout", "buildout_versions_file")
        buildout_cfg.remove_option("buildout", "extends")
        buildout_cfg.remove_option("buildout", "versions")
        buildout_cfg.remove_section("versions")
        if change_install_requires:
            unset_freezed_versions_in_install_requires(buildout_cfg)

@contextmanager
def revert_if_failed(keep_leftovers):
    from gitpy import LocalRepository
    from os import curdir
    repository = LocalRepository(curdir)
    get_tags = lambda: {tag.name:tag for tag in repository.getTags()}
    get_branches = lambda: {branch.name:branch for branch in repository.getBranches()}
    get_head = lambda branch_name: repository.getBranchByName(branch_name).getHead()
    get_status = lambda: dict(develop=get_head("develop"), master=get_head("master"), tags=get_tags(),
                              branches=get_branches())
    before = get_status()
    try:
        yield
    except:
        if keep_leftovers:
            raise
        now = get_status()
        for tag in set(now['tags']).difference(set(before['tags'])):
            repository.delete(now['tags'][tag])
        for branch in set(now['branches']).difference(set(before['branches'])):
            repository.delete(now['branches'][branch])
        for branch_name in ['master', 'develop']:
            repository.resetHard()
            branch = repository.getBranchByName(branch_name)
            repository.checkout(branch)
            repository.resetHard(before[branch_name])
        raise

def release_version_with_git_flow(version_tag, keep_leftovers=True):
    with revert_if_failed(keep_leftovers):
        _release_version_with_git_flow(version_tag)
