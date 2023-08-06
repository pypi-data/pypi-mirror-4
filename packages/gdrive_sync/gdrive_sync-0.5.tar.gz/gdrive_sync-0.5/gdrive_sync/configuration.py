"""
Deal with the configuration of sync files and api keys etc
"""
import os

CONFIGURATION_DIRECTORIES = ['~/.config/gdrive_sync', '~/gdrive_sync']
CONFIGURATION_FILE = 'configuration.ini'
CREDENTIALS_FILE = 'credentials'
CHANGES_DB = 'gdrive_changes.db'

# According to Google it is OK for installed applications to distribute the client secret 
# in the source code, see: https://developers.google.com/accounts/docs/OAuth2InstalledApp
# If you are reading this and considering using the below code for another program, then
# please create your own access code, it takes only about 2 minutes, see: 
# https://developers.google.com/drive/quickstart-python for information about how
CLIENT_ID = '848223844858.apps.googleusercontent.com'
CLIENT_SECRET = '6Drtud3KlYscfVhrAxZzyamY'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

class Configuration(object):
    def __init__(self, configuration_directory=None):
        if configuration_directory is None:
            configuration_directory = self.get_default_configuration_directory()
        self.configuration_directory = configuration_directory
        
        self.credentials_file = os.path.join(self.configuration_directory, CREDENTIALS_FILE)
        self.changes_file = os.path.join(self.configuration_directory, CHANGES_DB)
    
    def get_default_configuration_directory(self):
        # Check if any of the directories exist
        for path in CONFIGURATION_DIRECTORIES:
            pth = os.path.expanduser(path)
            if os.path.isdir(pth):
                return pth
        
        # No directory is present. Search for parent directories
        # and make our configuration directory in the first one
        # that exists
        for path in CONFIGURATION_DIRECTORIES:
            pth = os.path.expanduser(path)
            try:
                parent_pth = os.path.split(pth)[1]
                if os.path.isdir(parent_pth):
                    os.mkdir(pth)
                    return pth
            except OSError:
                continue
        
        raise OSError('Did not find configuration directory')
