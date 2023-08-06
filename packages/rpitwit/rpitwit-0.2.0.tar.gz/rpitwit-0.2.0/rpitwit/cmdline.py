"""
    The (very simple) Raspberry PI Remote Controller for Tweeter
    Version 0.2.0
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
import twitter
import os
import subprocess
import signal
import sys
from rpitwit_utils import *

def signal_handler(signal, frame):
  """
  Handler for SIGINT and SIGTERM signals.
  This is a good place to cleanup everything
  before exit.
  """
  print('\nStopping...');
  #TO DO: Add cleanup code for log database
  sys.exit(0)

def main(args=sys.argv[1:]):
  CONFIG_FILE = os.path.expanduser('~/.rpitwit_config')
  COMMAND_DIR = os.path.expanduser('~/rpitwit_commands')

  # Show help and exit
  if '--help' in args:
    print_help()
    sys.exit(0)

  # Show copyright info and exit
  if '--about' in args:
    print_about()
    sys.exit(0)

  # Register SIGINT and SIGTERM signal handlers.
  signal.signal(signal.SIGINT, signal_handler);
  signal.signal(signal.SIGTERM, signal_handler);

  # This is a beautiful way to load config files.
  # All the ugly code is now hidden under rpitwit_utils.py
  config_vars = {}
  if not os.path.exists(CONFIG_FILE) or '--load-defaults' in args:
    config_vars = use_defaults_and_create(CONFIG_FILE)
  else:
    config_vars = load_and_verify_settings(CONFIG_FILE,args)

  if not os.path.exists(COMMAND_DIR):
    print "Creating script directory on "+COMMAND_DIR
    try:
      os.makedirs(COMMAND_DIR)
      print "\n****************************************"
      print "Copy your shell or python scripts to the"
      print "script directory and execute them using:"
      print config_vars['magicword']+" <command> [args]"
      print "****************************************"
    except:
      print "\nNotice: Creation of script directory FAILED."
      print "Check the user permissions."
      sys.exit(1)

  twitter_stream = twitter.TwitterStream(
    auth=twitter.OAuth(
      config_vars['oauth_token'],
      config_vars['oauth_secret'],
      config_vars['CONSUMER_KEY'],
      config_vars['CONSUMER_SECRET']
    )
  )

  iterator = twitter_stream.statuses.filter(
    follow=config_vars['follow']
  )

  print "\nFollowing "+config_vars['follow']
  for tweet in iterator:
    if tweet.get('text'):
      if(tweet['text'].startswith(config_vars['magicword'])):
        args = tweet['text'].split(' ',1)
        if len(args)==1:
          print "Error: Command not especified."
        else:
          if '.\\' in args[1] or '..\\' in args[1]:
            print "Attempt to run a command outside sandbox DENIED."
          else:
            args = args[1].split(' ',1)
            if os.path.exists(COMMAND_DIR+'/'+args[0]):            
              print "Running command "+args[0]
              try:
                print subprocess.check_output(args=([(COMMAND_DIR+'/'+args[0])]+args[1:]))
              except:
                print "Error running command."
            elif os.path.exists(COMMAND_DIR+'/'+args[0]+'.py'):
              print "Running python script "+args[0]+'.py'
              try:
                print subprocess.check_output(args=(['python',(COMMAND_DIR+'/'+args[0])+'.py']+args[1:]))
              except:
                print "Error running python script."
            else:
              print "Command not found."
