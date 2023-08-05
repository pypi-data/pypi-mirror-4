import urllib
import commands
import os
import bbricks.output
import sys

import SCons.Defaults
import SCons.Builder

# - start - FIXME monkey patching, horribly messy, etc find a cleaner way to add lint support

OriginalShared = SCons.Defaults.SharedObjectEmitter
OriginalStatic = SCons.Defaults.StaticObjectEmitter

def file_in_list(needle_file, haystack):
    if not haystack:
        return False

    # find file as either relative or absolute path
    for f in haystack:
        if os.path.samefile(f, needle_file):
            return True

    return False

def DoLint(scons_env, source_node, target_node):

    # retrieve linted sources/headers from scons environment
    linted_sources = scons_env.bbricks_target.get('prefixed_sources',[])
    linted_headers = scons_env.bbricks_target.get('prefixed_headers',[])

    for source in source_node:

        cpp_path = source.srcnode().path
        if cpp_path in linted_sources:
            
            cpp_lint_node = scons_env.Lint(cpp_path + ".lint", source)
            for target in target_node:
                scons_env.Depends(target, cpp_lint_node)

            # attempt to guess header file
            header_path = os.path.splitext(cpp_path)[0] + ".h"
            if(header_path in linted_headers):
                header_lint_node = scons_env.Lint(header_path + ".lint", header_path)
                for target in target_node:
                    scons_env.Depends(target, header_lint_node)

def SharedObjectEmitter(target, source, scons_env):
    DoLint(scons_env, source, target)
    return OriginalShared(target, source, scons_env)

def StaticObjectEmitter(target, source, scons_env):
    DoLint(scons_env, source, target)
    return OriginalStatic(target, source, scons_env)

SCons.Defaults.SharedObjectEmitter = SharedObjectEmitter
SCons.Defaults.StaticObjectEmitter = StaticObjectEmitter

# - end - FIXME monkey patching, horribly messy, etc find a cleaner way to add lint support

def download_lint_script():
    temp_dir = ".tmp"
    if not os.path.exists(".tmp"):
        os.mkdir(temp_dir)

     # FIXME add a date check to download latest
    cpplint_path = ".tmp/cpplint.py"
    if os.path.exists(cpplint_path):
       return

    try:
        print 'downloading cpplint.py...'
        urllib.urlretrieve ("http://google-styleguide.googlecode.com/svn/trunk/cpplint/cpplint.py", cpplint_path)
        print 'downloading cpplint.py... done'
    except:
        abort_exec("error: could not download 'cpplint.py' check your internet connection")

    if not os.path.exists(cpplint_path):
        abort_exec("error: could not download 'cppling.py' check your internet connection")

def setup_scons_lint(scons_env, target):

    download_lint_script()

    scons_env.bbricks_target = target

    linter = SCons.Builder.Builder(
        action=['$PYTHON $LINT $LINT_OPTIONS $SOURCE','date > $TARGET'],
        suffix='.lint',
        src_suffix='.cpp')

    filter = target.get('lint_filter', None)
    

    scons_env.Append(BUILDERS={'Lint': linter})
    scons_env["PYTHON"] = sys.executable
    scons_env["LINT"] = ".tmp/cpplint.py"

    lint_options = ["--verbose=3"]

    if (filter):
        lint_options.append("--filter=%s" % filter)

    scons_env["LINT_OPTIONS"] = lint_options

def ensure_tab_free(path):
    """find any files with tabs, ignore gtest directory"""
    files_with_tabs = commands.getoutput("grep -l -I -E '\t' -r {0} | grep -v gtest | grep -v hg | grep -v *tags*".format(path))

    if len(files_with_tabs):
        bbricks.output.print_red("error: the following files have tabs. use spaces instead:")
        bbricks.output.abort_exec(files_with_tabs)
