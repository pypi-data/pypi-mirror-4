import bbricks
import base_profile

# Nacl 32 static library release profile

class StaticLibRelease(base_profile.Generic):

    def toolchain(self):
        nacl32_newlib_toolchain = {
            'CC':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/i686-nacl-gcc',
            'CXX':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/i686-nacl-g++',
            'AR':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/i686-nacl-ar',
            'LINK':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/i686-nacl-g++',
            'LD':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/i686-nacl-ld',
            'RANLIB':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/i686-nacl-ranlib',
        }
        return nacl32_newlib_toolchain

    def target_path(self, name):
        return self.target_staticlib_path(name)

    def install_path(self):
        return self.lib_path()

    def name(self):
        return 'nacl32_release'

    def description(self):
        return 'builds a nacl 32 release static library'

    def install_name(self):
        return 'nacl32'

    def type(self):
        return 'staticlib'

    def platform_options(self):

        options = [bbricks.configs.BASIC_OPTIONS,
                   bbricks.configs.NACL_OPTIONS,
                   bbricks.configs.NACL_RELEASE_OPTIONS,
                   bbricks.configs.NACL_STATIC_LIB_OPTIONS]

        return options

# Nacl 32 static library debug profile

class StaticLibDebug(StaticLibRelease):

    def name(self):
        return 'nacl32_debug'

    def description(self):
        return 'builds a nacl 32 debug static library'

    def platform_options(self):

        options = [bbricks.configs.BASIC_OPTIONS,
                   bbricks.configs.NACL_OPTIONS,
                   bbricks.configs.NACL_DEBUG_OPTIONS,
                   bbricks.configs.NACL_STATIC_LIB_OPTIONS]

        return options

# Nacl 32 nexe release profile

class NexeRelease(StaticLibRelease):

    def name(self):
        return 'nacl32_release'

    def description(self):
        return 'builds a nacl 32 release nexe'

    def type(self):
        return 'bin'

    def install_path(self):
        return self.bin_path()

    def target_path(self, name):
        return self.target_bin_path(name) + '.nexe'

    def platform_options(self):

        options = [bbricks.configs.BASIC_OPTIONS,
                   bbricks.configs.NACL_OPTIONS,
                   bbricks.configs.NACL_RELEASE_OPTIONS,
                   bbricks.configs.NACL_STATIC_LIB_OPTIONS,
                   bbricks.configs.NACL_STATIC_NEXE_OPTIONS]

        return options

# Nacl 32 nexe debug profile

class NexeDebug(NexeRelease):

    def name(self):
        return 'nacl32_debug'

    def description(self):
        return 'builds a nacl 32 debug nexe'

    def platform_options(self):

        options = [bbricks.configs.BASIC_OPTIONS,
                   bbricks.configs.NACL_OPTIONS,
                   bbricks.configs.NACL_DEBUG_OPTIONS,
                   bbricks.configs.NACL_STATIC_LIB_OPTIONS,
                   bbricks.configs.NACL_STATIC_NEXE_OPTIONS]

        return options


def Release(type='staticlib'):

    if type is 'staticlib':
        return StaticLibRelease()

    return NexeRelease()

def Debug(type='staticlib'):

    if type is 'staticlib':
        return StaticLibDebug()

    return NexeDebug()

