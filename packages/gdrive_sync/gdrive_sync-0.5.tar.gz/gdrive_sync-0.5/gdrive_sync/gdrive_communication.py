from __future__ import division
import os, random, time, json, webbrowser

import httplib2
from apiclient import errors
from apiclient.http import MediaFileUpload
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage

from .configuration import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

REQUEST_RATE_ERRORS = set(['rateLimitExceeded', 'userRateLimitExceeded'])
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'
MIME_DIRECTORY = 'application/vnd.google-apps.folder'
MIME_FILE = 'application/octet-stream'

FILE_FIELDS = ('id,title,mimeType,createdDate,modifiedDate,modifiedByMeDate,'
               'parents/id,originalFilename,fileExtension,fileSize,labels/trashed')
CHANGE_LIST_FIELDS = 'nextPageToken,largestChangeId,items(id,deleted,file(%s),fileId)' % FILE_FIELDS

# Default log function does nothing
log = lambda msg: None

def connect(credentials_file, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, oauth_scope=OAUTH_SCOPE, redirect_uri=REDIRECT_URI):
    """
    Connect to Google Drive. Will initiate a dialog with the user if 
    the application is not approved by the user yet
    """
    log('Logging in ...')
    
    ###########################
    # Get stored credential
    
    storage = Storage(credentials_file)
    credentials = storage.locked_get()
    
    if credentials is None:
        authenticate(credentials_file, client_id, client_secret, oauth_scope, redirect_uri)
        credentials = storage.locked_get()
        assert credentials is not None, 'User did not approve access to the drive'
    
    ###########################
    # Connect
    
    http = httplib2.Http()
    
    credentials = storage.locked_get()
    if credentials.access_token_expired:
        credentials.refresh(http)
    
    http = credentials.authorize(http)
    drive_service = build('drive', 'v2', http=http)
    
    storage.locked_put(credentials)
    
    log('DONE\n')
    return drive_service

def authenticate(credentials_file, client_id, client_secret, oauth_scope=OAUTH_SCOPE, redirect_uri=REDIRECT_URI):
    flow = OAuth2WebServerFlow(client_id, client_secret, oauth_scope, redirect_uri, access_type='offline')
    authorize_url = flow.step1_get_authorize_url()
    print 'I will open your browser where you must accept that the program'
    print 'gets access to your Google Drive. It will give you a code that'
    print 'you must input below'
    
    webbrowser.open(authorize_url, 2)
    
    code = raw_input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    
    # Check that the credentials work
    http = httplib2.Http()
    http = credentials.authorize(http)
    
    # Store the credentials
    storage = Storage(credentials_file)
    storage.locked_put(credentials)
    
def update(drive, database, max_changes_per_query=1000):
    """
    Update the change set database with any new changes on the Drive
    """
    
    def query_google_drive(request):
        t1 = time.time()
        results = call_with_exponential_backoff(request)
        items = results['items']
        
        if items:
            last = int(items[-1]['id'])
            largest = int(results['largestChangeId'])
            pst_done = (1 - (largest-last)/(largest-max_change_start)) * 100
            
            log(' Got %4d change items in %5.1f seconds (~%5.1f %% done)' % (len(items), time.time()-t1, pst_done))
        else:
            log(' No new changes found')
        
        return results, items
    
    log('Updating database ...')
    with database as db:
        max_change_start = db.max_change_id
        
        # Get new changes
        log(' Starting from change id %d' % (max_change_start+1))
        
        
        results = None
        num_downloaded = 0
        while True:
            if results is None:
                request = drive.changes().list(includeSubscribed=False,
                                               includeDeleted=True,
                                               pageToken=None,
                                               maxResults=max_changes_per_query,
                                               startChangeId=max_change_start+1,
                                               fields=CHANGE_LIST_FIELDS)
            else:
                request = drive.changes().list_next(request, results)
            
            # Are we done yet?
            if request is None:
                break
            
            # Download changes
            results, items = query_google_drive(request)
        
            # Store changes to database
            for change in items:
                db.add_change(change)
                num_downloaded += 1
    
    max_change_after = db.max_change_id    
    log('DONE: got %d changes, ended at change id %d\n' % (num_downloaded, max_change_after))

def upload(drive, filename, parent_id, is_directory=False, update=False, file_id=None):
    """
    Upload a file to a folder with a given ID. 
    
    If is_direcory is True then a directory is created and the file
    name must be the name of the directory
    """
    name = os.path.split(filename)[1]
    body = {'title': name, 'originalFilename': name, 'parents': [{'id': parent_id}]}
    
    if not update:
        assert file_id is None, 'You cannot specify the file id of a new file'
    
    if is_directory:
        media_body = None
        body['mimeType'] = MIME_DIRECTORY
        assert update is False, 'You cannot update a directory'
    else:
        media_body = MediaFileUpload(filename, mimetype=MIME_FILE, resumable=True)
        #body['mimeType'] = MIME_FILE
    
    #print filename, is_directory, body, update, file_id
    if update:
        request = drive.files().update(fileId=file_id, body=body, media_body=media_body)
    else:
        request = drive.files().insert(body=body, media_body=media_body)
    
    drive_file_info = call_with_exponential_backoff(request)
    return drive_file_info

def delete(drive, file_id, trash=True):
    """
    Either move a file to trash or permanently delete it
    """
    if trash:
        info = drive.files().get(fileId=file_id, fields=FILE_FIELDS)
        assert info['fileId'] == file_id
        request = drive.files().trash(fileId=file_id)
    else:
        request = drive.files().delete(fileId=file_id)
    return call_with_exponential_backoff(request)

def call_with_exponential_backoff(action):
    """
    Execute with exponential back-off
    Adapted from Googles API documentation
    """
    N = 5
    for n in range(N):
        try:
            return action.execute()
        except errors.HttpError as e:
            error = json.loads(e.content)
            # Get error code and type
            code = error.get('code')
            reason = error.get('error').get('errors')[0].get('reason')
            # Is this rate limiting errors?
            if n < N-1 and code == 403 and reason in REQUEST_RATE_ERRORS:
                # Apply exponential back-off.
                secs = (2 ** n) + random.randint(0, 1000) / 1000
                log('Google is limiting our query rate, backing off for %.2f seconds' % secs)
                time.sleep(secs)
            else:
                # Other error or end of tries, re-raise.
                raise
