import bbricks
import clang32_profile

# Clang 64 static library release profile

class StaticLibRelease(clang32_profile.StaticLibRelease):

    def name(self):
        return 'clang64_release'

    def description(self):
        return 'builds a clang 64 release static library'

    def install_name(self):
        return 'clang64'

    def platform_options(self):

        options = [bbricks.configs.BASIC_OPTIONS,
                   bbricks.configs.CLANG64_OPTIONS,
                   bbricks.configs.CLANG_RELEASE_OPTIONS]

        return options

# Clang 64 static library debug profile

class StaticLibDebug(clang32_profile.StaticLibDebug):

    def name(self):
        return 'clang64_debug'

    def description(self):
        return 'builds a clang 64 debug static library'

    def install_name(self):
        return 'clang64'

    def platform_options(self):

        options = [bbricks.configs.BASIC_OPTIONS,
                   bbricks.configs.CLANG64_OPTIONS,
                   bbricks.configs.CLANG_DEBUG_OPTIONS]

        return options

# Clang 64 release profile

class BinRelease(clang32_profile.BinRelease):

    def name(self):
        return 'clang64_release'

    def description(self):
        return 'builds a clang 64 release binary'

    def type(self):
        return 'bin'

    def install_name(self):
        return 'clang64'

    def platform_options(self):

        options = [bbricks.configs.BASIC_OPTIONS,
                   bbricks.configs.CLANG64_OPTIONS,
                   bbricks.configs.CLANG_RELEASE_OPTIONS]

        return options

# Clang 64 binary debug profile

class BinDebug(clang32_profile.BinDebug):

    def name(self):
        return 'clang64_debug'

    def description(self):
        return 'builds a clang 64 debug binary'

    def install_name(self):
        return 'clang64'

    def platform_options(self):

        options = [bbricks.configs.BASIC_OPTIONS,
                   bbricks.configs.CLANG64_OPTIONS,
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
