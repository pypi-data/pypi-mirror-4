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

import twitter
import sqlite3
import time
import os
import subprocess
import sys
from rpitwit_utils import *

config_vars = {}


CONFIG_FILE = os.path.expanduser('~/.rpitwit_config')
COMMAND_DIR = os.path.expanduser('~/rpitwit_commands')

def main(args=sys.argv[1:]):
  global config_vars,CONFIG_FILE,COMMAND_DIR
  # This is not the most beautiful way to load
  # the config file.... but it works.
  if not os.path.exists(CONFIG_FILE):
    keys = load_config(build_secret(),fromString=True)
    config_vars['oauth_token'],config_vars['oauth_secret'] = \
      twitter.oauth_dance('RPiTwit',keys['CONSUMER_KEY'],keys['CONSUMER_SECRET'])
    config_vars['magicword'] = '#rpitwit'
    config_vars['AppName'] = 'RPiTwit'
    twitter_handler = twitter.Twitter(auth=twitter.OAuth(config_vars['oauth_token'],config_vars['oauth_secret'],keys['CONSUMER_KEY'],keys['CONSUMER_SECRET']))
    config_vars['follow'] = find_userids(twitter_handler)
    write_config(config_vars,CONFIG_FILE)
    config_vars = dict(config_vars.items() + keys.items())
  else:
    config_vars = load_config(CONFIG_FILE)
    if not config_vars.get('magicword'):
      config_vars['magicword'] = '#rpitwit'
    keys = {}
    decodeKey = False
    if not config_vars.get('AppName') or not config_vars.get('CONSUMER_KEY') or not config_vars.get('CONSUMER_SECRET'):
      decodeKey = True
      keys = load_config(build_secret(),fromString=True)
      config_vars['AppName'] = 'RPiTwit'
    if not config_vars.get('follow'):
      twitter_handler = twitter.Twitter(auth=twitter.OAuth(config_vars['oauth_token'],config_vars['oauth_secret'],keys['CONSUMER_KEY'],keys['CONSUMER_SECRET']))
      config_vars['follow'] = find_userids(twitter_handler)
      write_config(config_vars,CONFIG_FILE) 
    config_vars = dict(config_vars.items() + keys.items())
    if not decodeKey:
      write_config(config_vars,CONFIG_FILE)

  if not os.path.exists(COMMAND_DIR):
    print "Creating script directory on "+COMMAND_DIR
    try:
      os.makedirs(COMMAND_DIR)
      print "Copy your shell or python scripts to the"
      print "script directory and execute them using:"
      print config_vars['magicword']+" <command> [args]"
    except:
      print "Creation of script directory FAILED."
      print "Check user permissions"
      sys.exit(1)


  twitter_stream = twitter.TwitterStream(auth=twitter.OAuth(config_vars['oauth_token'],config_vars['oauth_secret'],config_vars['CONSUMER_KEY'],config_vars['CONSUMER_SECRET']))

  iterator = twitter_stream.statuses.filter(follow=config_vars['follow'])

  print "Following to "+config_vars['follow']
  for tweet in iterator:
    if tweet.get('text'):
      if(tweet['text'].startswith(config_vars['magicword'])):
        args = tweet['text'].split(' ',1)
        if len(args)==1:
          print "Command not especified."
        else:
          if '.\\' in args[1] or '..\\' in args[1]:
            print "Attempt to run a command outside sandbox DENIED."
          else:
            args = args[1].split(' ',1)
            if os.path.exists(COMMAND_DIR+'/'+args[0]):            
              print "Running command "+args[0]
              print "Arguments"
              print ([(COMMAND_DIR+'/'+args[0])]+args[1:])
              try:
                print subprocess.check_output(args=([(COMMAND_DIR+'/'+args[0])]+args[1:]))
              except:
                print "Error running command"
            elif os.path.exists(COMMAND_DIR+'/'+args[0]+'.py'):
              print "Running python script "+args[0]+'.py'
              print "Arguments"
              try:
                print subprocess.check_output(args=(['python',(COMMAND_DIR+'/'+args[0])+'.py']+args[1:]))
              except:
                print "Error running python script"
            else:
              print "Command not found"

