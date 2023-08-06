#sudo easy_install colorama
import colorama
#sudo easy_install termcolor
import termcolor

import subprocess
import sys
import os

# colorama used for win32 compatibility in the future
colorama.init()

def print_red(message):
  print termcolor.colored(message, 'red')

def print_green(message):
  print termcolor.colored(message, 'green')

def print_yellow(message):
  print termcolor.colored(message, 'yellow')
    
def abort_exec(message):
  """abort execution of current script and output colored message"""
  print_red(message)
  sys.exit(1)

def abort_if_key_not_found(key, dictionary, error_message):
  if not dictionary.has_key(key):
    abort_exec(error_message)

def exec_or_die(interpreter, cmd, params, error_message):
  """execute command with given interpreter. abort if unsuccessful."""
  cmd_list = [interpreter, cmd] + params
  if(subprocess.call(cmd_list)):
    abort_exec(error_message)
  return

def assert_or_die(assertion, error_message):
  """abort script execution if assertion fails"""
  if not assertion:
    abort_exec(error_message)

def abort_if_none(variable, name):
  if not variable:
    abort_exec("%s is not set" % name)
