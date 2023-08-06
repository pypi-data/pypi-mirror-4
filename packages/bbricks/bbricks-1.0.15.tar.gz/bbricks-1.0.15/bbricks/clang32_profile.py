import bbricks
import base_profile

# Clang 32 static library release profile

class StaticLibRelease(base_profile.Generic):

    def toolchain(self):
        return bbricks.configs.CLANG_TOOLCHAIN

    def target_path(self, name):
        return self.target_staticlib_path(name)

    def install_path(self):
        return self.lib_path()

    def name(self):
        return 'clang32_release'

    def description(self):
        return 'builds a clang 32 release static library'

    def install_name(self):
        return 'clang32'

    def type(self):
        return 'staticlib'

    def platform_options(self):

        options = [bbricks.configs.BASIC_OPTIONS,
                   bbricks.configs.CLANG32_OPTIONS,
                   bbricks.configs.CLANG_RELEASE_OPTIONS]

        return options

# Clang 32 static library debug profile

class StaticLibDebug(StaticLibRelease):

    def name(self):
        return 'clang32_debug'

    def description(self):
        return 'builds a clang 32 debug static library'

    def platform_options(self):

        options = [bbricks.configs.BASIC_OPTIONS,
                   bbricks.configs.CLANG32_OPTIONS,
                   bbricks.configs.CLANG_DEBUG_OPTIONS]

        return options

# Clang 32 release profile

class BinRelease(StaticLibRelease):

    def name(self):
        return 'clang32_release'

    def description(self):
        return 'builds a clang 32 release binary'

    def type(self):
        return 'bin'

    def install_path(self):
        return self.bin_path()

    def target_path(self, name):
        return self.target_bin_path(name)

    def platform_options(self):

        options = [bbricks.configs.BASIC_OPTIONS,
                   bbricks.configs.CLANG32_OPTIONS,
                   bbricks.configs.CLANG_RELEASE_OPTIONS]

        return options

# Clang 32 binary debug profile

class BinDebug(BinRelease):

    def name(self):
        return 'clang32_debug'

    def description(self):
        return 'builds a clang 32 debug binary'

    def platform_options(self):

        options = [bbricks.configs.BASIC_OPTIONS,
                   bbricks.configs.CLANG32_OPTIONS,
                   bbricks.configs.CLANG_DEBUG_OPTIONS]

        return options


def Release(type='staticlib'):

    if type is 'staticlib':
        return StaticLibRelease()

    return BinRelease()


def Debug(type='staticlib'):

    if type is 'staticlib':
        return StaticLibDebug()

    return BinDebug()

