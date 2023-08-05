from Products.CMFCore.permissions import setDefaultRoles
import logging
from os import environ
from zope.app.component.hooks import getSite

PROJECTNAME = 'collective.validator.base'
SKINS_DIR = 'skins'
TITLE = 'Validator Tool'
DESCRIPTION = 'Validator for Plone'

GLOBALS = globals()

DEFAULT_ADD_TOOL_PERMISSION = "Use Validator Tool"
USE_VALIDATION_PERMISSION = PROJECTNAME + ": Launch portal validation"

setDefaultRoles(DEFAULT_ADD_TOOL_PERMISSION, ('Manager', 'Owner',))
setDefaultRoles(USE_VALIDATION_PERMISSION, ('Manager',))

#used to have a personal portal_url for the url of examined documents.
#if there is no VALIDATOR_PORTAL_URL environment variable, portal_url of the call is used.
ENV_PORTAL_URL = environ.get('VALIDATOR_PORTAL_URL','')

def getLogger(name,validator_filehandler=None):
    #create a separate logger for validation results
    logger = logging.getLogger(name)
    if validator_filehandler:
        #if i don't remove handlers, the messages will be duplicated
        [logger.removeHandler(x) for x in logger.handlers]
        logger.addHandler(validator_filehandler)
        logger.setLevel(2)
        #set the methods to print messages with new levels
        logger.validator_info = lambda x:logger.log(2, x)
        logger.validator_error = lambda x:logger.log(4, x)
    else:
        logger.setLevel(20)
        #set the methods to print messages with plone levels
        logger.validator_info = lambda x:logger.info(x)
        logger.validator_error = lambda x:logger.error(x)
    return logger

#set a separate log file. if there is no VALIDATOR_LOG_FILE environment
#variable, instance log as default
log_file= environ.get('VALIDATOR_LOG_FILE','')
if log_file:
    #create 2 more logging lvevels for the new logger
    logging.addLevelName(2, 'INFO')
    logging.addLevelName(4, 'ERROR')
    
    validator_filehandler = logging.FileHandler(log_file)
    #set new log start-level
    validator_filehandler.setLevel(2)
    
    formatter=logging.Formatter('%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S')
    validator_filehandler.setFormatter(formatter)

    logger = getLogger('collective.validator',validator_filehandler)
else:
    logger = getLogger('Plone')