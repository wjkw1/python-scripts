#!/usr/bin/python
#
# Men and mice get range utilisation statistics
# 
# Requirements:
#   - needs python3 for .xlsx report
# 
# For usage please execute: "$ python3 men_and_mice_report.py -h"
#
# Author: Western Wilson
#
import argparse
import getpass
import json
import logging
import pandas as pd
import re
import requests
import sys
import time
import urllib3
from urllib.parse import quote
from datetime import datetime

################################################################################
# Logging methods to standardise how threaded logs are written to, reminds me how to format strings nicely with methods
def log_error(message, exception=None):
  if exception is None:
    logging.error('FAILED at [{}] with no error message supplied'.format(message))
  else:
    logging.error('FAILED at [{}] error msg: {}'.format(message, exception))

def log_info(message):
  logging.info('{}'.format(message))

def log_debug(message):
  logging.debug('{}'.format(message))

################################################################################
# enum class for men & mice headers
class it:
    CUSTOM_PROPS = "customProperties"
    DESCRIPTION = "Description"
    FROM = "from"
    IS_SUBNET = "subnet"
    IS_CONTAINER = "isContainer"
    NAME = "name"
    SITE_CODE = "Site Code"
    TITLE =  "Title"
    TO = "to"
    UTILIZATION_PERCENTAGE = "utilizationPercentage"

################################################################################
# api wrapper class for easy api operations
class api:
  # An API GET call
  def getCall(url):
    try:
      myResponse = requests.get(url, auth=(username, password), verify=False)
    except:
      log_error('Failed get call for url: '+url)
      raise
      
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

    # Chance this will be big
    # TODO: think if it should be included or not???
    # log_debug('Output from postCall:' + str(myResponse.text))

    if myResponse.ok:
      rawreply = myResponse.content
      if not rawreply:
        return True
      else:
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
  
  ################################
  # Men & Mice specific API calls

  # Gets the current address space
  def getCurrentAddressSpace():
    logging.info("Starting getCurrentAddressSpace()")
    url="http://" + server + "/mmws/api/command/GetCurrentAddressSpace"
    try:
      r=api.getCall(url)
    except:
      raise
    logging.info("Finishing getCurrentAddressSpace()")
    return r

  # Set the address space using id
  def setAddressSpace(addressSpaceRef):
    logging.info("Starting setAddressSpace("+addressSpaceRef+")")
    url="http://" + server + "/mmws/api/command/SetCurrentAddressSpace"
    data= { "addressSpaceRef": addressSpaceRef }
    postData = json.dumps(data)
    try:
      api.postCall(url,postData)
    except:
      raise
    logging.info("Finishing setAddressSpace()")
  
  # Search for all addr spaces using id/name
  def getAddressSpaceFromUserInput(userInput):
    logging.info("Starting getAddressSpaceFromUserInput("+userInput+")")
    userInput = str(userInput)
    url="http://" + server + "/mmws/api/AddressSpaces"
    try:
      logging.debug("Check if user input is digit")
      if userInput.isdigit():
        logging.debug("YES a digit")
        nameVar = quote("\"AddressSpaces/"+str(userInput)+'"')
        url += "?filter=ref=%s" % (str(nameVar))
        r = api.getCall(url)
      else:
        logging.debug("NOT a digit")
        # Assume we have a name value here
        nameVar = quote("@\""+str(userInput)+"\"")
        url += "?filter=name=%s" % (str(nameVar))
        r = api.getCall(url)
    except:
      raise
    logging.info("Finishing getAddressSpaceFromUserInput("+userInput+")")
    return r

  # Get all of the address ranges
  def getRanges(limit=None):
    url="http://" + server + "/mmws/api/Ranges"

    if limit is not None:
        url += "/?limit="+str(limit)

    try:
        r = api.getCall(url)
    except:
        raise
    return r


################################################################################
# Main methods to compartmentalise the script

# Selects an address space from the user input, function used to keep main clean
def selectAddressSpaceFromUserInput(userInput):
  logging.info("Starting selectAddressSpaceFromUserInput("+userInput+")")
  try:
    # Gets the address space ID and Name, assumes an there will always be an existing address space
    currentAddressSpace = api.getCurrentAddressSpace()
    currAddrSpaceID = currentAddressSpace['addressSpaceRef'].split("/")[1]
    # Get the new intended address space and name
    currentAddressSpace = api.getAddressSpaceFromUserInput(currAddrSpaceID)
    currAddrSpaceName = currentAddressSpace['addressSpaces'][0]['name']

    # Set newAddressSpace as None so if its not set we can fallout gracefully
    newAddressSpace = None
    # Check if the currAddrSpace matches, if it doesn't then try find a match
    if userInput.isdigit():
      if currAddrSpaceID == userInput:
        logging.info("Current address space is already selected: {"+str(currAddrSpaceID)+" : "+str(currAddrSpaceName)+"}")
      else:
        newAddressSpace = api.getAddressSpaceFromUserInput(userInput)
    else:
      newAddressSpace = api.getAddressSpaceFromUserInput(userInput)
    
    # Set the address space if we need to, otherwise through fallout error
    if newAddressSpace is not None:
        if newAddressSpace['totalResults'] != 0:
            newAddressSpaceID = newAddressSpace['addressSpaces'][0]['ref']
            # Set the new adress space
            api.setAddressSpace(newAddressSpaceID)
            logging.info("Address space updated successfully: {"+str(newAddressSpace['addressSpaces'][0])+"}")
            # TODO: Add a way for user to select from list of multiple address spaces if more than one return
        else:
            logging.info("Address space not found for user input: '" + userInput+"', please try another input")
            quit()
  except Exception as e:
      log_error("selectAddressSpaceFromUserInput('"+userInput+"')",e)
      quit()

  logging.info("Finishing selectAddressSpaceFromUserInput("+userInput+")")

################################################################################

def init(argv):
  # global variables so we don't have to pass them everywhere
  global username
  global password
  global start_time
  global server
  global address_space

  # Set debug to False by default
  global debug
  debug = False

  # Setup the logger
  logging.basicConfig(
    filename='./logs/output.log',
    filemode='a',
    # encoding='utf-8', # This does not work
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO
  )
  # Set the logger again as sometimes it keeps debug mode ???
  logging.getLogger().setLevel(logging.INFO)

  start_time = datetime.now()
  
  print("***START SCRIPT***")
  logging.info("***START SCRIPT***")

  # Check the command line parameters are good:
  parser = argparse.ArgumentParser(description='Provide a list of devices in a file with your M&M_USERNAME and we\'ll return build a report')
  parser.add_argument('-s', required=True, metavar='HOSTNAME', help='M&M server hostname or IP address')
  parser.add_argument('-u', required=True, metavar='USERNAME', help='M&M username')
  parser.add_argument('-a', required=True, metavar="ADDRESS_SPACE", help="Address Space ID or Name")
  parser.add_argument('-d', action="store_true", help='Enable debug mode')
  
  args = parser.parse_args(argv)

  server = args.s
  username = args.u
  address_space = args.a

  print(args)
  logging.info(args)

  if args.d:
    logging.getLogger().setLevel(logging.DEBUG)

  password = getpass.getpass(prompt='Password:')

  logging.debug('Finished initialising script ')

################################################################################


def main(argv):
  # Just make these global so I don't have to keep passing them around
  global username
  global password
  global server
  global address_space

  # initialise the script
  init(argv)

  # Set the address space
  selectAddressSpaceFromUserInput(address_space)

  # Get the ranges report
  ranges = api.getRanges()

  # Build the ranges report
  rangesArr = ranges['ranges']
  minimisedRanges = []

  log_info('Starting looping through ranges')
  for range in rangesArr:
    # temp variable to use for each loop to append to array
    tempRangeAttributes = {}

    # Check the customProperties exist and if so add to report
    customProperties = range[it.CUSTOM_PROPS]
    if it.TITLE in customProperties:
        tempRangeAttributes[it.TITLE] = range[it.CUSTOM_PROPS][it.TITLE]
    if it.DESCRIPTION in customProperties:
        tempRangeAttributes[it.DESCRIPTION] = range[it.CUSTOM_PROPS][it.DESCRIPTION]
    if it.SITE_CODE in customProperties:
        tempRangeAttributes['SiteCode'] = range[it.CUSTOM_PROPS][it.SITE_CODE]

    # Check for utilization, name and if is subnet
    if it.UTILIZATION_PERCENTAGE in range:
        tempRangeAttributes[it.UTILIZATION_PERCENTAGE] = range[it.UTILIZATION_PERCENTAGE]
    if it.NAME in range:
        tempRangeAttributes[it.NAME] = range[it.NAME]
    if it.IS_SUBNET in range:
        tempRangeAttributes[it.IS_SUBNET] = range[it.IS_SUBNET]
    if it.IS_CONTAINER in range:
        tempRangeAttributes[it.IS_CONTAINER] = range[it.IS_CONTAINER]
    if it.FROM in range:
        tempRangeAttributes[it.FROM] = range[it.FROM]
    if it.TO in range:
        tempRangeAttributes[it.TO] = range[it.TO]

    # append to ranges
    minimisedRanges.append(tempRangeAttributes)
  log_info('Finished looping through ranges')

  # create the data frame
  # print report to file
  columns = (
    it.NAME, it.TITLE, 'SiteCode',
    it.DESCRIPTION, it.UTILIZATION_PERCENTAGE,
    it.FROM,it.TO,it.IS_SUBNET,
    it.IS_CONTAINER
  )
  df = pd.DataFrame(data=minimisedRanges, columns=columns)
  
  # Used to fix a bug with illegal characters
  df = df.applymap(lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)

  # Start building the report
  log_info('Starting build of report')
  reportFileName = "ip_range_utilisation_output.xlsx"
  with pd.ExcelWriter(reportFileName) as writer:
    df.to_excel(writer, index=False, sheet_name='ALL')
  log_info("Completed building report: '" + reportFileName + "'")

  global start_time
  # calculate script execution time
  run_time = datetime.now() - start_time
  
  print("***END SCRIPT***")
  logging.info("***END SCRIPT***")
  logging.info("Script execution time:  "+ str(run_time))
  print("Script execution time:  "+ str(run_time))
  
################################################################################

if __name__ == "__main__":
   main(sys.argv[1:])
