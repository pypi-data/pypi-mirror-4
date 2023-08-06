"""Configures and builds c/c++ source, given target configurations."""

import sys
import os
import subprocess

#sudo easy_install termcolor
import termcolor

# FIXME how to import correctly so pylint does not complain?
import SCons.Script

import bbricks.output
import bbricks.config_schema
import bbricks.lint

class Builder:
    """Builds C/C++, given a list of target configurations.

    Attributes:
        target_list: A list of all possible target configurations (see bbricks.config_schema for details).
    """
    def __init__(self, target_list):
        """Inits Builder targets map to track validated configurations."""
        bbricks.output.abort_if_none(target_list, 'target_list')

        self.__targets = self.__map_targets(target_list)
        self.__scons_env = SCons.Script.Environment()
        
    @staticmethod
    def __expand_target(target, targets):
        """Ensure target is valid and playing nice with other targets in build.

        Args:
            target: target configuration to validate before resolutions.
            targets: a list of all other targets in build

        Returns:
            None"""
        
        valid_target = bbricks.config_schema.process_configuration(target)

        target_name = valid_target['name']
        if targets.has_key(target_name):
            error = 'name "%s" used in more than ' % target_name
            bbricks.output.abort_exec(error)

        return valid_target

    @staticmethod
    def print_banner(banner):
        """Prints build banner in yellow.

        Args:
            banner: A string with any text to display as build banner.

        Returns:
            None."""
        if not banner:
            return

        bbricks.output.print_yellow(banner)


    @staticmethod
    def __map_targets(target_list):
        """Creates a dict mapping names to targets.

        Args:
            target_list: A list of target configuration dicts.

        Returns:
            A dict mapping target names to build configurations.
        """
        targets = {}
        for target in target_list:
            target_name = target['name']
            
            expanded_target = Builder.__expand_target(target, targets)
            
            targets[target_name] = expanded_target

        return targets

    def print_available_targets(self):
        """Prints a list of all available targets with descriptions."""

        print '\navailable targets are:\n'

        for key in sorted(self.__targets.keys()):
            target = self.__targets[key]
            name = termcolor.colored(target['name'], 'green')
            print("%s: %s" % (name, target['description']))

        print ''

    def get_target(self, name):
        """Gets a target dict given its name"""

        if name not in self.__targets.keys():
            self.print_available_targets()
            error = "error: could not find target \"%s\"\n" % name
            bbricks.output.abort_exec(error)

        return self.__targets[name]

    def target_exists(self, name):
        """Check if target dict given its name"""

        return name in self.__targets.keys()

    def valid_arguments(self, targets):
        """Validates the list of target names chosen to build.

        Args:
            A list of target names to build"""

        if len(targets) < 1:
            self.print_available_targets()
            SCons.Script.SetOption('help', True)
            return False

        if len(targets) > 1:
            error = 'error: you can only build one target at a time'
            bbricks.output.abort_exec(error)

        return True

    @staticmethod
    def build_dependency(path, target_name):
        """build dependency at location

        Args:
            path: path to SConstruct file
            target_name: target to build
        """

        parent_path = os.getcwd()
        os.chdir(path)

        arguments = sys.argv[1:-1]
        
        build_failed = subprocess.call(['scons'] + arguments + [target_name])
        os.chdir(parent_path)
        error = 'error: could not build %s:%s' % (path, target_name) 
        bbricks.output.assert_or_die(build_failed == 0, error)

    @staticmethod
    def ensure_file_exists(path):
        """check file exists, abort execution otherwise

        Args:
            path: check this file path exists
        """

        exists = os.path.exists(path)
        print('checking ' + path + ' exists... ' + str(exists))
        error = "error: %s is not installed on your machine" % path
        bbricks.output.assert_or_die(exists, error)

    @staticmethod
    def resolve_dependency(path, target_name):
        """resolve external build ependencies

        Args:
            path: can be either file or directory. files are checked for existance. directories invoke scons on it.
            target_name: target name to invoke in dependency
        """

        if os.path.isfile(path):
            Builder.ensure_file_exists(path)
            return

        if os.path.isdir(path):
            Builder.build_dependency(path, target_name)
            return

        bbricks.output.abort_exec("error: dependency %s is neither a file nor a directory" % path)

    @staticmethod
    def __resolve_dependencies(target):
        """Build or check external dependencies

        Args:
            target: target dict to resolve dependencies for
        """
        
        if not target.has_key('depends'):
            return

        deps = target['depends']
        target_name = target['name']
        if isinstance(deps, str):
            Builder.resolve_dependency(deps, target_name)
            return

        if isinstance(deps, list):
            for dep in deps:
                Builder.resolve_dependency(dep, target_name)
            return

        # FIXME move to schema validation
        error = "error: 'depends' is neither a list nor string"
        bbricks.output.abort_exec(error)

    def __setup_toolchain(self, target):
        """Setup build toolchain for target.

        Args:
            target: target dict with toolchain"""

        self.__scons_env.Replace(**target['toolchain'])

    def __add_build_options(self, target):
        """Add all build options (ie. compiler flags).

        Args:
            target: target dict with all options."""

        for options in target['options']:    
            self.__scons_env.Append(**options)

    @staticmethod
    def __add_multiple_job_support():
        """Configure scons to start as many jobs as cores"""

        num_cpu = int(os.environ.get('NUM_CPU', 2))
        SCons.Script.SetOption('num_jobs', num_cpu)

    @staticmethod
    def __setup_scons_variant_dir(target):
        """Setup a scons variant """

        source_root = target['root']
        prefixed_root = target['prefix']

        SCons.Script.VariantDir(prefixed_root, source_root, duplicate=0)

    @staticmethod
    def __create_build_dir(target):
        """Creates build direcotry if needed

        Args:
            target: target dict with all options."""

        build_dir = target['prefix']
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)

    def __install_files(self, target):
        """Set scons up to export/install files
        
        Args:
            target: target dict with all options."""


        if not target.has_key('install'):
            return

        all_sources = target.get('prefixed_ugly_sources', []) + \
                      target.get('prefixed_sources', [])

        for install_item in target['install']:
            error = "error: install item without 'destination'"
            bbricks.output.assert_or_die(install_item.has_key('destination'),
                                         error)

            error = "error: install item without 'source'"
            bbricks.output.assert_or_die(install_item.has_key('source'), error)

            source = install_item['source']
            destination = install_item['destination']

            install_node = None

            if os.path.isdir(source):
                install_node =  self.__scons_env.InstallAs(destination,
                                                           [source])
            else:
                install_node =  self.__scons_env.Install(destination,
                                                         source)

            # NOTE: make sure we don't try to set a dependency on the
            # actual library/binary, or else we create a circular
            # dependency
            if not source == target['target']:
                self.__scons_env.Depends(all_sources, install_node)

            # NOTE: we need to add an alias/shortcut in two scenarions
            # 1. we are not building a binary, but would still like to
            #    install headers
            # 2. we are building a binary
            if (target['type'] == 'ignore' and       \
                not source == target['target']) or   \
                                                     \
               (not target['type'] == 'ignore' and   \
                source == target['target']):
                self.__scons_env.Alias(target['name'], install_node)

    def __setup_scons_post_actions(self, target):
        """Set scons up to execute post build actions
        
        Args:
            target: target dict with all options."""

        post_actions = target.get('post_actions',[])

        for action in post_actions:
            self.__scons_env.AddPostAction(target['target'], action)

    def __setup_scons_build(self, target):
        """Set scons up to build either exec or staticlib
        
        Args:
            target: target dict with all options."""

        sources = target.get('prefixed_ugly_sources', []) + target.get('prefixed_sources', [])

        build_node = None
        if  target['type'] == 'bin':
            build_node = self.__scons_env.Program(target=target['target'],
                                                  source=sources)

        if  target['type'] == 'staticlib':
            build_node = self.__scons_env.StaticLibrary(target=target['target'],
                                                        source=sources)

        if not build_node is None:

            # NOTE: alias build name to target so we can do things like:
            # scons my_pretty_target_name
            self.__scons_env.Alias(target['name'], build_node)


    def __setup_scons_lint(self, target):
        """Set scons up to lint source

        Args:
            target: target dict with all options."""

        bbricks.lint.setup_scons_lint(self.__scons_env, target)

    def build(self, target_names, banner=None):
        """FIXME docstring
        """

        self.print_banner(banner)

        if not self.valid_arguments(target_names):
            return

        # NOTE: get first target, since we
        # currently support building only one target
        # at a time

        target = self.get_target(target_names[0])

        self.__resolve_dependencies(target)
        self.__setup_toolchain(target)
        self.__add_build_options(target)
        self.__add_multiple_job_support()
        self.__create_build_dir(target)
        self.__install_files(target)
        self.__setup_scons_lint(target)
        self.__setup_scons_build(target)
        self.__setup_scons_post_actions(target)
        self.__setup_scons_variant_dir(target)

def get_build_option_value(option_name):
    """Get command line option (ie. --some-option)

    Args:
        option_name: For example, if you passed --some-option
        then use 'some-option'"""

    value = SCons.Script.GetOption(option_name)
    if value is None:
        return ''
    return value

def add_build_bool_option(option_name, default_value, help_message):
    """FIXME docstring"""
    SCons.Script.AddOption('--' + option_name,
                           action = 'store_true',
                           dest = option_name,
                           default = default_value,
                           help = help_message)

def add_build_string_option(option_name, default_value, help_message):
    """FIXME docstring"""
    SCons.Script.AddOption('--' + option_name,
                           default = default_value,
                           dest = option_name,
                           nargs = 1,
                           type = 'string',
                           action = 'store',
                           help = help_message)

def add_build_option(option_name, default_value, help_message):
    """Support command a line option (ie. --some-option).

    Args:
        option_name: For example, if you passed --some-option
            then use 'some-option'.
        default_value: Some default value in case not explictly
            specified.
        help_message: A useful help message to display with --help"""

    if isinstance(default_value, str):
        add_build_string_option(option_name, default_value, help_message)
        return

    if isinstance(default_value, bool):
        add_build_bool_option(option_name, default_value, help_message)
        return

    error = "error: add_build_option accepts only \
                default bool or string for %s" % option_name
    output.abort_exec.format(error)

def create_environment(target_list):
    """FIXME docstring
    """
    return Builder(target_list)

# FIXME move banner to environment creation
def build_target(builder, targets, optional_banner=None):
    """FIXME docstring
    """

    builder.build(targets, optional_banner)
