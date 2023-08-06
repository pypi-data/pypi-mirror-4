import bbricks
import nacl32_profile

# Nacl 64 static library release profile

class StaticLibRelease(nacl32_profile.StaticLibRelease):

    def toolchain(self):
        nacl64_newlib_toolchain = {
            'CC':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-gcc',
            'CXX':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-g++',
            'AR':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-ar',
            'LINK':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-g++',
            'LD':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-ld',
            'RANLIB':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-ranlib',
        }
        return nacl64_newlib_toolchain

    def name(self):
        return 'nacl64_release'

    def description(self):
        return 'builds a nacl 64 release static library'

    def install_name(self):
        return 'nacl64'

# Nacl 64 static library debug profile

class StaticLibDebug(nacl32_profile.StaticLibDebug):

    def toolchain(self):
        nacl64_newlib_toolchain = {
            'CC':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-gcc',
            'CXX':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-g++',
            'AR':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-ar',
            'LINK':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-g++',
            'LD':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-ld',
            'RANLIB':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-ranlib',
        }
        return nacl64_newlib_toolchain

    def name(self):
        return 'nacl64_debug'

    def description(self):
        return 'builds a nacl 64 debug static library'

    def install_name(self):
        return 'nacl64'

# Nacl 64 nexe release profile

class NexeRelease(nacl32_profile.NexeRelease):

    def toolchain(self):
        nacl64_newlib_toolchain = {
            'CC':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-gcc',
            'CXX':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-g++',
            'AR':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-ar',
            'LINK':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-g++',
            'LD':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-ld',
            'RANLIB':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-ranlib',
        }
        return nacl64_newlib_toolchain

    def name(self):
        return 'nacl64_release'

    def description(self):
        return 'builds a nacl 64 release nexe'

    def install_name(self):
        return 'nacl64'

# Nacl 64 nexe debug profile

class NexeDebug(nacl32_profile.NexeDebug):

    def toolchain(self):
        nacl64_newlib_toolchain = {
            'CC':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-gcc',
            'CXX':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-g++',
            'AR':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-ar',
            'LINK':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-g++',
            'LD':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-ld',
            'RANLIB':'/opt/nacl_sdk/pepper_20/toolchain/*_x86_newlib/bin/x86_64-nacl-ranlib',
        }
        return nacl64_newlib_toolchain

    def name(self):
        return 'nacl64_debug'

    def description(self):
        return 'builds a nacl 64 debug nexe'

    def install_name(self):
        return 'nacl64'


def Release(type='staticlib'):

    if type is 'staticlib':
        return StaticLibRelease()

    return NexeRelease()

def Debug(type='staticlib'):

    if type is 'staticlib':
        return StaticLibDebug()

    return NexeDebug()

