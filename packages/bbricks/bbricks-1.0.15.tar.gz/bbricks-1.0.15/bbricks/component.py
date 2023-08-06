import os
import bbricks

def add_liking_libraries(target, libs):

    libs_options = {
        'LIBS':[]
    }

    for lib in libs:
        libs_options['LIBS'].append(lib)

    all_options = target.get('options',[])
    all_options.append(libs_options)

    target['options'] = all_options

def verify_property(component=None, property=None):

    if component is None:
        bbricks.output.abort_exec("component needs to be defined")

    if component.get(property, None) is None:
        bbricks.output.abort_exec("component missing '%s' in SConstruct file" % property)


def verify_one_property(dictionary=None, properties=[]):

   one_found = False

   for pname in properties:
       if dictionary.get(pname, None):
           one_found = True
           break

   if one_found:
     return

   properties_str = ''
   for pname in properties:
       properties_str += "'" + pname + "' "

   bbricks.output.abort_exec("you need at least one of %s in your dictionary" % properties_str)

def verify_component(component):

    verify_one_property(dictionary=component, properties=['name'])
    verify_one_property(dictionary=component, properties=['type'])

def verify_target(target):

    verify_one_property(dictionary=target, properties=['sources','ugly_sources'])


def add_sources_file(target=None, property='sources', source_file=''):

   if os.path.exists(source_file):

       if target.get(property,None) is None:
           target[property] = []

       target[property].append(source_file)


def verify_one_file_exists(files=[]):

   one_found = False

   for fname in files:
       if os.path.exists(fname):
           one_found = True
           break

   if one_found:
     return

   files_str = ''
   for fname in files:
       files_str += fname + ' '

   bbricks.output.abort_exec("you need at least one of these %s in your config directory" % files_str)


def add_crossplatform_sources(target=None):

  if target is None:
      bbricks.output.abort_exec("you need a defined target to add sources to")

  verify_one_file_exists(['crossplatform.sources',
                          'ugly_crossplatform.sources'])

  add_sources_file(target, 'sources', 'crossplatform.sources')
  add_sources_file(target, 'ugly_sources', 'ugly_crossplatform.sources')


def generate_install_hierachy(target, repo_root, install_root):

    #eg. path/to/repo/umbrella/component
    component_location = os.path.abspath('../../')

    #eg. path/to/repo
    common_prefix = os.path.commonprefix([component_location, repo_root])

    #eg. umbrella/component
    header_export_prefix = component_location.replace(common_prefix,'')[1:]

    #eg. path/to/global/build/nacl32/include/umbrella/component
    install_hierarchy = os.path.join(install_root, 'include', header_export_prefix)

    return install_hierarchy


def add_default_install_entry(target, repo_root, install_root):

    # create a bbricks list of public header exports and add to target. for example:
    #[
    #  {
    #    'destination': 'path/to/global/build/nacl32/include/core/office/odraw',
    #    'source': '../public/header1.h'
    #  },
    #  {
    #    'destination': 'path/to/global/build/nacl32/include/core/office/odraw/subdir',
    #    'source': '../public/subdir/odraw.h'
    #  },
    #]

    INSTALL_INCLUDE_PATH = generate_install_hierachy(target, repo_root, install_root)

    public_exports = []
    for root, dirs, files in os.walk('../public'):
        for fname in files:

            # eg. ../public/subdir/odraw.h
            fullpath = os.path.join(root, fname)

            # eg. subdir
            flatpath = os.path.dirname(fullpath.replace('../public/',''))

            # eg. path/to/global/build/nacl32/include/core/office/odraw/subdir
            install_dir = os.path.join(INSTALL_INCLUDE_PATH,flatpath)

            install_entry = {
                'source':fullpath,
                'destination': install_dir,
            }

            target['install'].append(install_entry)

def create_target(component, profile):

    target = {
        'name' : profile.name(),
        'description' : profile.description(),
        'toolchain' : profile.toolchain(),
        'options' : profile.options(component.get('options',{})),
        'type' : profile.type(),
        'target' : profile.target_path(component['name']),
        'install' : [{
            'source' : profile.target_path(component['name']),
            'destination' : profile.install_path(),
        }],
        'depends' : component.get('depends',[]),
        'platform' : {
            'install_root' : profile.install_root()
        }
    }

    add_liking_libraries(target, component.get('link',[]))
    add_crossplatform_sources(target)
    add_default_install_entry(target,
                              profile.repo_root(),
                              profile.install_root())

    bbricks.component.verify_target(target)

#     pp = pprint.PrettyPrinter(indent=4)
#     pp.pprint(target)


    return target
