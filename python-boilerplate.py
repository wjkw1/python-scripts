#!/usr/bin/python
#
# Boilerplate script for using flags with some good base imports to include. Also has some example api calls.
# 
# Requirements:
#   - needs python3 for .xlsx report
# 
# For usage please execute: "$ python3 python-boilerplate.py -h"
#
# Author: Western Wilson
#
import argparse
import getpass
import json
import logging
import os
import re
import requests
import sys
import time
from datetime import datetime

# Logging methods to standardise how threaded logs are written to, reminds me how to format strings nicely with methods
def log_error(message, exception=None):
  if exception is None:
    logging.error('FAILED at [{}] with no error message supplied'.format(message))
  else:
    logging.error('FAILED at [{}] error msg: {}'.format(message, exception))

def log_info(message):
  print(message)
  logging.info('{}'.format(message))

def log_debug(message):
  logging.debug('{}'.format(message))

# api wrapper class for easy api operations
class api:
  # An API GET call
  def getCall(url):
    try:
      myResponse = requests.get(url, auth=(username, password), verify=False)
    except:
      log_error('Failed get call for url: '+url)
      raise
      exit()
      
    log_debug('Output from postCall:' + myResponse.text)

    if(myResponse.ok):
      rawreply = myResponse.content
      jNAData = json.loads(rawreply.decode())
      return jNAData['result']
    elif myResponse.status_code == 404:
      log_error('API get call 404 Error!: '+url)
      exit()
    else:
      log_error('API get call other status code Error!: '+url)
      raise Exception(jNAData['error']['message'])

# An API POST call
  def postCall(url,postData):

    log_debug('Calling postData: '+postData)
    
    headers = {'Content-type': 'application/json', 'Accept': '*/*'}
    try:
      myResponse = requests.post(url, auth=(username, password), data=postData, headers=headers, verify=False)
    except Exception as e:
      message = 'Failed post call for url: '+ str(url)
      log_error(message,e)
      exit()

    log_debug('Output from postCall:' + myResponse.text)

    if myResponse.ok:
      rawreply = myResponse.content
      jNAData = json.loads(rawreply.decode())
      return jNAData['result']
    elif myResponse.status_code == 404:
      log_error('API Error 404!')
      exit()
    else:
      rawreply = myResponse.content
      jNAData = json.loads(rawreply.decode())
      log_error('API Error unknown header!')
      raise Exception(jNAData['error']['message'])
      exit()

################################################################################

def init(argv):
  # global variables so we don't have to pass them everywhere
  global username
  global password
  global input_filename
  global start_time

  # Set debug to False by default
  global debug
  debug = False
  
  if not os.path.exists('./logs'):
    os.makedirs('./logs')
    
  # Setup the logger
  logging.basicConfig(
    filename='./logs/output.log',
    filemode='a',
    # encoding='utf-8', # This does not work
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt="%H:%M:%S",
    level=logging.INFO
  )
  # Set the logger again as sometimes it keeps debug mode ???
  logging.getLogger().setLevel(logging.INFO)

  start_time = datetime.now()
  
  log_info("***START SCRIPT***")

  # Check the command line parameters are good:
  parser = argparse.ArgumentParser(description='Provide a list of devices in a file with your SBX_USERNAME and we\'ll return build a report')
  parser.add_argument('-u', required=True, metavar='username', help='CouchDB Username')
  parser.add_argument('-f', required=True, metavar='input-file.csv', help="The csv input file of devices to insert.")
  parser.add_argument('-d', action="store_true", help='Enable debug mode')
  
  args = parser.parse_args(argv)
  
  username = args.u
  input_filename = args.f

  log_info(args)

  if args.d:
    logging.getLogger().setLevel(logging.DEBUG)

  #TODO: double check that the input file is a csv file
  input_filename = args.f
  log_info(input_filename)

  password = getpass.getpass(prompt='Password:')


def main(argv):
  # Just make these global so I don't have to keep passing them around
  global username
  global password
  global server

  init(argv)
  # TODO: Do the useful stuff
  
  global start_time
  # calculate script execution time
  run_time = datetime.now() - start_time
  
  log_info("***END SCRIPT***")
  log_info("Script execution time:  "+ str(run_time))
  
################################################################################

if __name__ == "__main__":
   main(sys.argv[1:])
