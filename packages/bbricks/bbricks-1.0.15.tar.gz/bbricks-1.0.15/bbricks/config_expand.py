"""Helps expand properties in target configurations."""

import os
import fnmatch
import operator

import bbricks.output

def get_files_in_dir(path, filter_by='*'):
    """Creates a list of files found in path (recursively).

     Args:
        path: String with path to directory.
        filter: String with pattern to filter files with.

     Returns:
        A list with all files found in path (recursively)."""

    sources = []
    root, filenames = operator.itemgetter(0, -1)(os.walk(path).next())
    for filename in fnmatch.filter(filenames, filter_by):
        file_entry = os.path.join(root, filename)
        absolute_file_entry = os.path.abspath(file_entry)
        sources.append(absolute_file_entry)

    return sources

def load_source_list_from_file(path):
    """Creates a list of files from a text file.

    Args:
        path: String with path to file.

    Returns:
        A list iwth all files listed in the file"""

    if not isinstance(path, str):
        error = 'error: load_source_list_from_file expects a path string'
        bbricks.output.abort_exec(error)

    try:
        list_file = open(path, 'r')
        sources = list_file.readlines()

        # FIXME removing newlines can be cleaner
        for i in xrange(len(sources)):
            file_entry = sources[i].replace('\n', '')
            absolute_file_entry = os.path.abspath(file_entry)
            sources[i] = absolute_file_entry

        return sources
    except IOError:
        bbricks.output.abort_exec('error: could not read ' + path)

    return []

def get_source_list(prop_name, target):
    """Gets a resolved list of source files from a target dict.
     Args:
        prop_name: String with source property name.
        target: A dict target configuration."""
        
    source_files = []
    if not target.has_key(prop_name):
        return source_files

    for source in target[prop_name]:
        if os.path.isdir(source):
             # FIXME pass only one filter with both cases
            source_files += get_files_in_dir(source,'*.cpp')
            source_files += get_files_in_dir(source,'*.cc')
        elif source.split(".")[-1] == 'sources':
            source_files += load_source_list_from_file(source)
        else:
            absolute_path = os.path.abspath(source)
            source_files.append(absolute_path)

    return source_files

def resolve_target_sources(target):
    """Converts all heterogeneous source lists into homogenenous equivalent.

    Args:
      target: Target to resolve.

    Returns:
      None."""
    sources = get_source_list('sources', target)
    if len(sources):
        target['sources'] = sources

    ugly_sources = get_source_list('ugly_sources', target)
    if len(ugly_sources):
        target['ugly_sources'] = ugly_sources

    # FIXME shift check to schema
    if not target.has_key('sources') and not target.has_key('ugly_sources'):
        error = 'sources and ugly_sources missing in target'
        bbricks.output.abort_exec(error)


def add_source_root(target):
    """Add source root if not explicitly added in target configuration.

    Args:
        target: A dict target configuration."""
    if target.has_key('root'):
        return

    sources = target.get('ugly_sources', []) + target.get('sources', [])
    prefix = os.path.commonprefix(sources)

    target['root'] = os.path.dirname(prefix)

def expand_source_root(target):
    """FIXME docstring
    """

    target['root'] = os.path.abspath(target['root'])

def add_build_prefix(target):
    """Get build dir for target

    Args:
        target: target dict

    Returns:
        Constructed build directory"""

    target['prefix'] = os.path.join("build", target['name'])

    
def prefix_paths(root, prefix, paths):
    """Replace root path with prefix for every path.

    Args:
        root: Replace root.
        prefix: With prefix.
        paths: List with all paths.

    Returns:
        A list with all prefixed paths"""

    prefixed_paths = []
    if not paths:
        return prefixed_paths

    for path in paths:
        prefixed_path = path.replace(root, prefix)
        prefixed_paths.append(prefixed_path)

    return prefixed_paths

def prefix_source_paths(target):
    """Prefixes all paths with variant path.

    Args:
        target: A dict target configuration."""

    prefixed_sources = prefix_paths(target['root'],
                                    target['prefix'],
                                    target.get('sources',None))
    if prefixed_sources:
        target['prefixed_sources'] = prefixed_sources

    prefixed_ugly_sources = prefix_paths(target['root'],
                                         target['prefix'],
                                         target.get('ugly_sources',None))
    if prefixed_ugly_sources:
        target['prefixed_ugly_sources'] = prefixed_ugly_sources

def guess_prefixed_headers(target):
    """Guess prefixed headers from compiled sources

    Args:
        target: A dict target configuration."""

    sources = target.get('sources',[])
    headers = []
    for source in sources:
        header = os.path.splitext(source)[0] + ".h"

        if (os.path.exists(header)):
            headers.append(header)

    prefixed_headers = prefix_paths(target['root'],
                                    target['prefix'],
                                    headers)

    target['prefixed_headers'] = prefixed_headers

def preprocess_install_items(target):
    """Ensures that only one directory is installed as the destination directory. For all others, expand the directory content into individual files and install to destination.

    Args:
        target: A dict target configuration."""

    processed_items = []

    dirs_found = {}
    for install_item in target.get('install',[]):
        error = "error: install item without 'destination'"
        bbricks.output.assert_or_die(install_item.has_key('destination'),
                                     error)

        error = "error: install item without 'source'"
        bbricks.output.assert_or_die(install_item.has_key('source'), error)

        source = install_item['source']
        destination = install_item['destination']

        # are we already installing a directory on to a directory?
        # if so, expand into a list of files to install
        if dirs_found.has_key(destination) and os.path.isdir(source):
            files = get_files_in_dir(source)

            for file in files:
                install_file = {
                                 'source': file,
                                 'destination': destination
                                }

                processed_items.append(install_file)

            continue
            
        dirs_found[destination] = source

        processed_items.append(install_item)

    target['install'] = processed_items
