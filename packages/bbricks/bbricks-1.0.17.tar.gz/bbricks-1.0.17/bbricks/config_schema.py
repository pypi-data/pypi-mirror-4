import bbricks.output
import bbricks.config_expand

PROPERTY_SCHEMA = [
  'name',
  'description',
  'optional',
  'type',
  'example'
]

EXTENDS_PROPERTY_SCHEMA = {
  'name':'extends',
  'description':'Inherits all properties from parent configuration.',
  'example':'\'extends\':SOME_PARENT_CONFIG',
  'optional':True,
  'type':'dictionary'
}

NAME_PROPERTY_SCHEMA = {
  'name':'name',
  'description':'Name given to target configuration, later used when invoking scons. For example: scons some_project_linux_x86_32_release',
  'example':'\'name\':\'some_project_linux_x86_32_release\'',
  'optional':False,
  'type':'string'
}

DESCRIPTION_PROPERTY_SCHEMA = {
  'name':'description',
  'description':'Description given to target configuration, later used when invoking scons with no arguments.',
  'example':'\'description\':\'builds an awesome target for linux x86 arch 32 bits\'',
  'optional':False,
  'type':'string'
}

OPTIONS_PROPERTY_SCHEMA = {
  'name':'options',
  'description':'A list of dictionaries. FIXME (better description)',
  'example':'\'options\':[OPTIONS_1, OPTIONS_2, OPTIONS_3]',
  'optional':True,
  'type':'list'
}

TARGET_PROPERTY_SCHEMA = {
  'name':'target',
  'description':'Path and name to either exectuable or library built. For libaries, omit \'lib\' and \'.a\'',
  'example':'\'target\':\'path/to/libray\'',
  'optional':False,
  'type':'string'
}

ROOT_PROPERTY_SCHEMA = {
  'name':'root',
  'description':'Root path for location of sources. FIXME (better description, perhaps rename to root_path?)',
  'example':'\'root\':\'path/to/root/containing/source\'',
  'optional':True,
  'type':'string'
}

# TODO (alvaro): check for either ugly_sources or sources. fail build if neither is present.
UGLY_SOURCES_PROPERTY_SCHEMA = {
  'name':'ugly_sources',
  'description':'Source not cpplinted. Heterogeneous list of either path to sourcefile.cpp, path to directory, or path to file.sources. Can be used in conjunction with \'sources\'.',
  'example':'\'ugly_sources\':[\'sourcefile.cpp\',\'path/to/some/dir\',\'file.sources\']',
  'optional':True,
  'alternate':'sources',
  'type':'list'
}

# TODO (alvaro): check for either ugly_sources or sources. fail build if neither is present.
SOURCES_PROPERTY_SCHEMA = {
  'name':'sources',
  'description':'Cpplinted_source. Heterogeneous list of either path to sourcefile.cpp, path to directory, or path to file.sources. Can be used in conjunction with \'sources\'.',
  'example':'\'sources\':[\'sourcefile.cpp\',\'path/to/some/dir\',\'file.sources\']',
  'alternate':'ugly_sources',
  'optional':True,
  'type':'list'
}

INSTALL_PROPERTY_SCHEMA = {
  'name':'install',
  'description':'List of dictionaries describing files to install.',
  'example':'\'install\':{\'source\':\'path/to/some/libsomething.a\',\'destination\':\'some/path/to/lib32\'}',
  'optional':True,
  'type':'list'
}

CONFIG_SCHEMA = [
   EXTENDS_PROPERTY_SCHEMA,
   NAME_PROPERTY_SCHEMA,
   DESCRIPTION_PROPERTY_SCHEMA,
   OPTIONS_PROPERTY_SCHEMA,
   TARGET_PROPERTY_SCHEMA,
   ROOT_PROPERTY_SCHEMA,
   UGLY_SOURCES_PROPERTY_SCHEMA,
   SOURCES_PROPERTY_SCHEMA,
   INSTALL_PROPERTY_SCHEMA
]

def validate_property_schema(property_schema):
  for key in PROPERTY_SCHEMA:
    bbricks.output.abort_if_key_not_found(key, property_schema, '\'%s\' missing from property schema' % key)

def build_config_schema():
  config_schema = {}
  for property_schema in CONFIG_SCHEMA:
    validate_property_schema(property_schema)
    key = property_schema['name']
    config_schema[key]=property_schema
  return config_schema

def class_to_config_type(property):
  if isinstance(property, str):
    return 'string'

  if isinstance(property, bool):
    return 'boolean'

  if isinstance(property, dict):
    return 'dictionary'

  if isinstance(property, list):
    return 'list'

  return 'unknown'

def validate_property(key, config, config_schema):

  property_schema = config_schema[key]
  # make sure mandatory properties exists
  if not property_schema['optional'] and not config.has_key(key):
    bbricks.output.abort_exec('\'%s\' missing from configuration' % key)

  # optional property not found, no need to continue
  if not config.has_key(key):
    return

  # check right type is passed
  property = config[key]
  type = property_schema['type']

  if not class_to_config_type(property) == type:
    bbricks.output.abort_exec('\'%s\' should be a %s' % (key,type))

def validate_configuration(configuration):
  config_schema = build_config_schema()

  for key in config_schema.iterkeys():
    validate_property(key, configuration, config_schema)

def build_inheritance_list(configuration, configuration_list):

  if(configuration == None):
    bbricks.output.abort_exec('cannot append to null configuration_list')

  configuration_list.insert(0, configuration)
  if(configuration.has_key('extends')):
    build_inheritance_list(configuration['extends'], configuration_list)

  return configuration_list

def merge_configuration(source_configuration, destination_configuration):
  for key in source_configuration:
    if isinstance(source_configuration[key], list):
      if not destination_configuration.has_key(key):
        destination_configuration[key] = []
      destination_configuration[key] += source_configuration[key][:]
    else:
      destination_configuration[key] = source_configuration[key]

def extend_configuration(configuration):

  inheritance_list = []
  inheritance_list = build_inheritance_list(configuration, inheritance_list)

  inherited_configuration = {}

  for configuration in inheritance_list:
    merge_configuration(configuration, inherited_configuration)

  return inherited_configuration

def process_configuration(configuration):
  processed_config = extend_configuration(configuration)

  bbricks.config_expand.resolve_target_sources(processed_config)
  bbricks.config_expand.add_source_root(processed_config)
  bbricks.config_expand.expand_source_root(processed_config)
  bbricks.config_expand.add_build_prefix(processed_config)
  bbricks.config_expand.prefix_source_paths(processed_config)
  bbricks.config_expand.guess_prefixed_headers(processed_config)
  bbricks.config_expand.preprocess_install_items(processed_config)

  # NOTE comment out to view resolved target
  # import pprint
  # pprint.pprint(processed_config)

  validate_configuration(processed_config)

  return processed_config

# CONFIG_03 = {
#   'name':'config03',
#   'target':'target01',
#   'description':'description01',
#   'root':'root01'
# }

# CONFIG_02 = {
#   'name':'config02',
#   'extends': CONFIG_03
# }

# CONFIG_01 = {
#   'name':'config01',
#   'extends': CONFIG_02,
# }

# process_configuration(CONFIG_01)
