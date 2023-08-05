import os

class Generic:

    @staticmethod
    def repo_root():

        cwd = os.path.abspath('.')

        repo_dir = os.path.dirname(cwd)

        while (repo_dir != os.path.dirname(repo_dir) and
               not os.path.exists(os.path.join(repo_dir, ".git")) and
               not os.path.exists(os.path.join(repo_dir, ".hg")) and
               not os.path.exists(os.path.join(repo_dir, ".svn"))):
            repo_dir = os.path.dirname(repo_dir)

        return repo_dir

    @staticmethod
    def __get_install_umbrella():

        repository_root = Generic.repo_root()
        install_root = os.path.join(repository_root,'..','build')

         #eg. /abs/path/to/global/build
        return os.path.abspath(install_root)


    def target_staticlib_path(self, name):
        #ie. path/to/umbrella/component/config/build/nacl32release/lib/libcomponent.a
        return os.path.join('build', self.name(), 'lib' + name + '.a')

    def target_bin_path(self, name):
        #ie. path/to/umbrella/component/config/build/nacl32release/bin/component
        return os.path.join('build', self.name(), 'bin', name)

    def install_root(self):
        #ie. path/to/global/install/nacl32
        return os.path.join(self.__get_install_umbrella(), self.install_name())

    def include_path(self):
        #ie. path/to/global/install/nacl32/include
        return os.path.join(self.install_root(), 'include')

    def lib_path(self):
        #ie. path/to/global/install/nacl32/lib
        return os.path.join(self.install_root(), 'lib')

    def bin_path(self):
        #ie. path/to/global/install/nacl32/bin
        return os.path.join(self.install_root(), 'bin')

    def options(self, additional_options = {}):

        #add default include and lib path
        general_options = {
            'CCFLAGS' : ['-isystem' + self.include_path()],
            'LIBPATH' : self.lib_path()
        }

        all_options = self.platform_options() + [general_options,
                                                 additional_options]

        return all_options
