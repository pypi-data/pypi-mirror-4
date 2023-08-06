#################
# COMMON OPTIONS
#################

BASIC_OPTIONS = {
    'CCFLAGS':['-Wall','-Wfatal-errors']
}

STRICT_OPTIONS = {
    'CCFLAGS':['-Werror']
}

#################
#  NACL CONFIGS
#################

PNACL_TC_BIN_DIR = '/opt/nacl_sdk/pepper_24/toolchain/*_x86_pnacl/newlib/bin/'

PNACL_NEWLIB_TOOLCHAIN = {
    'CC':PNACL_TC_BIN_DIR + 'pnacl-clang',
    'CXX':PNACL_TC_BIN_DIR + 'pnacl-clang++',
    'AR':PNACL_TC_BIN_DIR + 'pnacl-ar',
    'LINK':PNACL_TC_BIN_DIR + 'pnacl-clang++',
    'LD':PNACL_TC_BIN_DIR + 'pnacl-ld',
    'RANLIB':PNACL_TC_BIN_DIR + 'pnacl-ranlib',
    'TRANSLATE':PNACL_TC_BIN_DIR + 'pnacl-translate',
    'STRIP':PNACL_TC_BIN_DIR + 'pnacl-strip'
}

NACL32_NEWLIB_TOOLCHAIN = {
    'CC':'/opt/nacl_sdk/pepper_21/toolchain/*_x86_newlib/bin/i686-nacl-gcc',
    'CXX':'/opt/nacl_sdk/pepper_21/toolchain/*_x86_newlib/bin/i686-nacl-g++',
    'AR':'/opt/nacl_sdk/pepper_21/toolchain/*_x86_newlib/bin/i686-nacl-ar',
    'LINK':'/opt/nacl_sdk/pepper_21/toolchain/*_x86_newlib/bin/i686-nacl-g++',
    'LD':'/opt/nacl_sdk/pepper_21/toolchain/*_x86_newlib/bin/i686-nacl-ld',
    'RANLIB':'/opt/nacl_sdk/pepper_21/toolchain/*_x86_newlib/bin/i686-nacl-ranlib',
}

NACL64_NEWLIB_TOOLCHAIN = {
    'CC':'/opt/nacl_sdk/pepper_21/toolchain/*_x86_newlib/bin/x86_64-nacl-gcc',
    'CXX':'/opt/nacl_sdk/pepper_21/toolchain/*_x86_newlib/bin/x86_64-nacl-g++',
    'AR':'/opt/nacl_sdk/pepper_21/toolchain/*_x86_newlib/bin/x86_64-nacl-ar',
    'LINK':'/opt/nacl_sdk/pepper_21/toolchain/*_x86_newlib/bin/x86_64-nacl-g++',
    'LD':'/opt/nacl_sdk/pepper_21/toolchain/*_x86_newlib/bin/x86_64-nacl-ld',
    'RANLIB':'/opt/nacl_sdk/pepper_21/toolchain/*_x86_newlib/bin/x86_64-nacl-ranlib',
}

PNACL_OPTIONS = {
    'CPPDEFINES':'NACL'
}

PNACL_RELEASE_OPTIONS = {
    'CCFLAGS':'-O2'
}

PNACL_STATIC_LIB_OPTIONS = {
    'CCFLAGS':['-fdata-sections','-ffunction-sections'],
}

PNACL_STATIC_PEXE_OPTIONS = {
    'CCFLAGS':['-std=gnu++98',
               '-pthread',
               '-D_GNU_SOURCE=1',
               '-D__STDC_FORMAT_MACROS=1',
               '-D_BSD_SOURCE=1',
               '-D_POSIX_C_SOURCE=199506',
               '-D_XOPEN_SOURCE=600',
               '-fno-stack-protector',
               '-fomit-frame-pointer',
               '-static',
               '-DNACL'],
    'LIBS':['ppapi_cpp',
            'ppapi'
            ]
}

NACL_STATIC_NEXE_OPTIONS = {
    'CCFLAGS':['-std=gnu++98',
               '-pthread',
               '-D_GNU_SOURCE=1',
               '-D__STDC_FORMAT_MACROS=1',
               '-D_BSD_SOURCE=1',
               '-D_POSIX_C_SOURCE=199506',
               '-D_XOPEN_SOURCE=600',
               '-fno-stack-protector',
               '-fomit-frame-pointer',
               '-static',
               '-DNACL'],
    'LINKFLAGS' : ['--gc-sections'],
    'LIBS':['ppapi_cpp',
            'ppapi'
            ]
}

NACL_OPTIONS = {
    'CPPDEFINES':'NACL'
}

NACL_RELEASE_OPTIONS = {
    'CCFLAGS':'-O2'
}

NACL_DEBUG_OPTIONS = {
    'CCFLAGS':['-g','-O0']
}

NACL_STATIC_LIB_OPTIONS = {
    'CCFLAGS':['-fdata-sections','-ffunction-sections'],
    'LINKFLAGS':['--gc-sections']
}


#################
#  GCC CONFIG
#################

GCC_TOOLCHAIN = {
    'CC':'gcc',
    'CXX':'g++',
    'AR':'ar',
    'LINK':'g++',
    'LD':'ld',
    'RANLIB':'ranlib'
}

GCC32_OPTIONS = {
    'CCFLAGS' : ['-m32', '-march=i386'],
    'LINKFLAGS' : ['-m32', '-march=i386']
}

GCC64_OPTIONS = {
    'CCFLAGS' : ['-m64', '-march=core2'],
    'LINKFLAGS' : ['-m64', '-march=core2']
}

GCC_DEBUG_OPTIONS = {
    'CCFLAGS':['-g','-O0']
}

#################
#  IOS CONFIG
#################

IOS_5_1_DEVICE_STATIC_LIB_OPTIONS = {
    'CCFLAGS' : ['-arch', 'armv7',
                 '-mthumb',
                 '-miphoneos-version-min=5.1',
                 '-Wno-overloaded-virtual',
                 '-isysroot',
                 '/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS5.1.sdk',
                 '-I/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/usr/llvm-gcc-4.2/lib/gcc/arm-apple-darwin10/4.2.1/include',
                 '-I/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS5.1.sdk/usr/include/c++/4.2.1',
                 '-I/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS5.1.sdk/usr/include'
                 ]
}

IOS_5_1_SIMULATOR_STATIC_LIB_OPTIONS = {
    'CCFLAGS' : ['-arch', 'i386',
                 '-miphoneos-version-min=5.1',
                 '-Wno-overloaded-virtual',
                 '-isysroot','/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator5.1.sdk',
                 '-I/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/usr/llvm-gcc-4.2/lib/gcc/i686-apple-darwin11/4.2.1/include',
                 '-I/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator5.1.sdk/usr/include/c++/4.2.1',                
                 '-I/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator5.1.sdk/usr/include'
                 ]
}

#################
#  CLANG CONFIG
#################


CLANG_TOOLCHAIN = {
    'CC':'clang',
    'CXX':'clang++',
}

CLANG32_OPTIONS = {
    'CCFLAGS' : ['-m32', '-march=i386'],
    'LINKFLAGS' : ['-m32', '-march=i386']
}

CLANG64_OPTIONS = {
    'CCFLAGS' : ['-m64'],
    'LINKFLAGS' : ['-m64']
}

CLANG_STATIC_LIB_OPTIONS = {
    'CCFLAGS':['-fdata-sections','-ffunction-sections'],
    'LINKFLAGS':['--gc-sections']
}

CLANG_CODE_COVERAGE_OPTIONS = {
    'CCFLAGS' : ['-fprofile-arcs','-ftest-coverage']
}

CLANG_DEBUG_OPTIONS = {
    'CCFLAGS':['-g','-O0']
}

CLANG_RELEASE_OPTIONS = {
    'CCFLAGS':'-Os'
}



#################
#  PREDEFINED BUILDS - NACL
#################

NACL32_NEWLIB_STATIC_RELEASE_LIB = {
  'description':'builds a nacl 32 bit static release library',
  'toolchain':NACL32_NEWLIB_TOOLCHAIN,
  'options':[BASIC_OPTIONS,
             NACL_OPTIONS,
             NACL_RELEASE_OPTIONS,
             NACL_STATIC_LIB_OPTIONS
             ],
  'type':'staticlib'
}

# FIXME (adding for backwards compatibility, remove once builds are updated)
NACL32_NEWLIB_STATIC_LIB = NACL32_NEWLIB_STATIC_RELEASE_LIB

NACL64_NEWLIB_STATIC_RELEASE_LIB = {
  'description':'builds a nacl 32 bit static release library',
  'toolchain':NACL64_NEWLIB_TOOLCHAIN,
  'options':[BASIC_OPTIONS,
             NACL_OPTIONS,
             NACL_RELEASE_OPTIONS,
             NACL_STATIC_LIB_OPTIONS
             ],
  'type':'staticlib'
}

PNACL_NEWLIB_STATIC_RELEASE_LIB = {
  'description':'builds a pnacl static release library using the pnacl newlib toolchain',
  'toolchain':PNACL_NEWLIB_TOOLCHAIN,
  'options':[BASIC_OPTIONS,
             NACL_OPTIONS,
             NACL_RELEASE_OPTIONS,
             NACL_STATIC_LIB_OPTIONS
             ],
  'type':'staticlib'
}

#################
#  PREDEFINED BUILDS - CLANG
#################

CLANG32_STATIC_DEBUG_LIB =  {
  'description':'builds a clang 32 bit static debug library',
  'toolchain':CLANG_TOOLCHAIN,
  'options':[BASIC_OPTIONS,
             CLANG32_OPTIONS,
             CLANG_DEBUG_OPTIONS
            ],
  'type':'staticlib'
}

# FIXME (adding for backwards compatibility, remove once builds are updated)
CLANG32_STATIC_LIB = CLANG32_STATIC_DEBUG_LIB
# FIXME (adding for backwards compatibility, remove once builds are updated)
CLANG32_LIB =  CLANG32_STATIC_DEBUG_LIB

CLANG64_STATIC_DEBUG_LIB = {
  'description':'builds a clang 64 bit static debug library',
  'toolchain':CLANG_TOOLCHAIN,
  'options':[BASIC_OPTIONS,
             CLANG64_OPTIONS,
             CLANG_DEBUG_OPTIONS
            ],
  'type':'staticlib'
}

# FIXME (adding for backwards compatibility, remove once builds are updated)
CLANG64_STATIC_LIB = CLANG64_STATIC_DEBUG_LIB

CLANG64_STATIC_CODE_COVERAGE_LIB = {
  'description':'builds a clang 64 bit static debug library with code coverage enabled',
  'toolchain':CLANG_TOOLCHAIN,
  'options':[BASIC_OPTIONS,
             CLANG64_OPTIONS,
             CLANG_DEBUG_OPTIONS,
             CLANG_CODE_COVERAGE_OPTIONS
            ],
  'type':'staticlib'
}

CLANG32_STATIC_RELEASE_LIB =  {
  'description':'builds a clang 32 bit static debug library',
  'toolchain':CLANG_TOOLCHAIN,
  'options':[BASIC_OPTIONS,
             CLANG32_OPTIONS,
             CLANG_RELEASE_OPTIONS
            ],
  'type':'staticlib'
}

CLANG64_STATIC_RELEASE_LIB = {
  'description':'builds a clang 64 bit static debug library',
  'toolchain':CLANG_TOOLCHAIN,
  'options':[BASIC_OPTIONS,
             CLANG64_OPTIONS,
             CLANG_RELEASE_OPTIONS
            ],
  'type':'staticlib'
}

#################
#  PREDEFINED BUILDS - IOS
#################

IOS_5_1_SIMULATOR_STATIC_DEBUG_LIB = {
  'description':'builds a IOS 32 bit static debug library for iOS Simulator',
  'toolchain':CLANG_TOOLCHAIN,
  'options':[BASIC_OPTIONS,
             CLANG32_OPTIONS,
             CLANG_RELEASE_OPTIONS,
             IOS_5_1_SIMULATOR_STATIC_LIB_OPTIONS
            ],
  'type':'staticlib' 
}

IOS_5_1_DEVICE_STATIC_RELEASE_LIB = {
  'description':'builds a IOS 32 bit static release library for IOS device',
  'toolchain':CLANG_TOOLCHAIN,
  'options':[BASIC_OPTIONS,
             CLANG32_OPTIONS,
             CLANG_RELEASE_OPTIONS,
             IOS_5_1_DEVICE_STATIC_LIB_OPTIONS
            ],
  'type':'staticlib'  
}

IOS_5_1_DEVICE_STATIC_DEBUG_LIB = {
    'description':'builds a IOS 32 bit static debug library for IOS device',
    'toolchain':CLANG_TOOLCHAIN,
    'options':[BASIC_OPTIONS,
               CLANG32_OPTIONS,
               CLANG_DEBUG_OPTIONS,
               IOS_5_1_DEVICE_STATIC_LIB_OPTIONS
               ],
    'type':'staticlib'
}
