"""
    The (very simple) Raspberry PI Remote Controller for Tweeter
    Copyright (C) 2013  Mario Gomez (fuenteabierta.teubi.co)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


def load_config(source,fromString=False):
  """
    Loads a config file with configuration lines in the form:
       key=value
    And returns a dictionary with the format:
       {
         'key':'value'
       }
    The config file must exist or it will generate an assertion
    error.
    If you specify fromString=True it just parses the lines from
    the script provided as parameter on "source"
    
    Warning: This function can read empty files and will return
    empty dictionaires, also if you have two lines with the same 
    key it will overwrite the previous value with the last value
    found in the file.
  """
  contents = ''
  if not fromString:
    import os
    assert os.path.exists(source)
    f = open(source,'r')
    contents = f.read()
    f.close()
  else:
    contents = source
 
  config_vars = {}

  lines = contents.split('\n')
  for line in lines:
    config_pair = line.split('=')
    if(len(config_pair)==2):
      config_vars[config_pair[0].strip()] = config_pair[1].strip()
  return config_vars

def write_config(config_vars,destination):
  """
    Writes a dictionary as a config file
    returns True if write was successful
    False if not
  """
  assert type(config_vars)==dict
  result = True
  try:
    f = open(destination,'w')
    for key,value in config_vars.iteritems():
      f.write(key)
      f.write('=')
      f.write(value)
      f.write('\n')
    f.close()
  except:
    result = False
  return result

def build_secret():
  """
  build_secret()
  Decodes the application keys for tweeter,
  this function is here only to comply with 
  tweeter application keys usage guidelines,
  that require me to not distribuite the keys
  in plain text.
  It's very trivial to recover the keys, but I
  warn you: this keys had "read only" access
  to the Twitter API, you must generate your
  own keys if you want to add more features
  that require a higher access level.
  You can generate your own keys following
  the instructions
  included with the documentation.
  """
  import base64
  keys = '\
Q09OU1VNRVJfS0VZID0gZFE0ZHQ1SFdH\
Z09XNGJTdjNjTjV3IApDT05TVU1FUl9T\
RUNSRVQgPSA3aU5zM3pKM0pFdVpaNWhi\
NTNUbldNSXFERUlzZ3k2aGVqaU9OQmFF\
WQ=='
  return base64.b64decode(keys)

def find_userids(twitter_handler):
  """
  This function asks for twitter usernames
  and returns a string with the user ids
  separated by commas.
  """
  newUsers = ''
  while(newUsers==''):
    print "\nPlease write the username(s) wich do you want to"
    print "authorize to send commands (separated by commas):"
    users = raw_input()
    users = users.split(',')
    for user in users:
      try:
        print "Trying to get userid for "+user
        data = twitter_handler.users.show(screen_name=user.strip())
        if newUsers=='':
          newUsers = str(data['id'])
        else:
          newUsers = newUsers+','+str(data['id'])
        print "User @"+user+" added to the list."
      except:
        print "Error: Failed to add "+user+" to the list."
  return newUsers

