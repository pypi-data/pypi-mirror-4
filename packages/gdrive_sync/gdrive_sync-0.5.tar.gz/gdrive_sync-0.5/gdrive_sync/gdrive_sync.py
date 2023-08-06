import os, datetime
from tzlocal import get_localzone

from .configuration import Configuration
from .change_db import ChangeDB, GDriveFile, GDriveDirectory
from . import gdrive_communication as api

class GDriveSyncError(Exception):
    pass

SYSTEM_TZ = get_localzone()

class GDriveSyncDifference(object):
    ONLY_LOCAL = 'only_local'
    ONLY_REMOTE = 'only_remote'
    NEWER_LOCAL = 'newer_local'
    FILES_ARE_DIFFERENT = 'files_differ'
    FILE_DIRECTORY_MISMATCH = 'type_mismatch'

    def __init__(self, reason, remote_file=None, local_file=None):
        self.reason = reason
        self.remote_file = remote_file
        self.local_file = local_file
      
class LocalItem(object):
    def __init__(self, path, is_dir=False, is_file=False, size=False, modified=None, file_size=None):
        self.path = path
        self.is_dir = is_dir
        self.is_file = is_file
        self.size = size
        self._modified = modified
        self._file_size = file_size
        
    @property
    def modified(self):
        if self._modified is None:
            t = os.path.getmtime(self.path)
            self._modified =  datetime.datetime.fromtimestamp(t, SYSTEM_TZ)
        return self._modified
    
    @property
    def file_size(self):
        if self._file_size is None:
            self._file_size = os.path.getsize(self.path)
        return self._file_size
  
class GDriveSync():
    def __init__(self, configuration_directory=None, verbose=False):
        self.config = Configuration(configuration_directory)
        self.change_db = ChangeDB(self.config.changes_file, logger=self.log)
        self.verbose = verbose
        self.root = None
        api.log = self.log
        self.logged_warnings = []
        self.logged_errors = []
        
    def connect(self):
        """
        Connect and authenticate with the Google Drive web service 
        """
        self.drive = api.connect(credentials_file=self.config.credentials_file)
        
    def update(self):
        """
        Update the local change database with any changes made to the Drive since last update
        """
        api.update(self.drive, self.change_db)
        
    def build_file_tree(self):
        """
        Build the google Drive file tree from the change list
        """
        self.change_db.read()
        self.root = self.change_db.get_file_tree()
        
    def upload_file(self, remote_base_dir, local_base_dir, local_file, update=False, dry_run=False):
        """
        Upload a file (optionally update file that is already there)
        """
        # Get name on drive
        rel_path = os.path.relpath(os.path.abspath(local_file),
                                   os.path.abspath(local_base_dir))
        rel_path = rel_path.replace(os.pathsep, '/')
        if rel_path == '.':
            drive_path = remote_base_dir
        else: 
            drive_path = remote_base_dir + '/' + rel_path
            
        # Get parent id on drive
        drive_dir = os.path.split(drive_path)[0]
        print 'looking for', drive_dir
        parent = self.root.get_child(drive_dir)
        print 'parent is', parent.path
        
        if os.path.isdir(local_file):
            assert not update, 'Cannot update a directory'
            
            self.log('Creating directory %s in %s' % (drive_path, drive_dir))
            if dry_run:
                return
            
            try:
                info = api.upload(self.drive, local_file, parent.id, is_directory=True)
                return
            except api.errors.HttpError as e:
                self.log('Cannot create directory %s' % local_file, 'warning')
                self.log(e.message)
                
            newdir = GDriveDirectory(info, parent)
            parent.add_child(newdir)
            #print info
        
        elif update:
            self.log('Updating file %s to %s' % (drive_path, drive_dir))
            if dry_run:
                return
            
            item = self.root.get_child(drive_path)
            
            try:
                _info = api.upload(self.drive, local_file, parent.id, update=True, file_id=item.id)
            except api.errors.HttpError as e:
                self.log('Cannot update file %s' % local_file, 'warning')
                self.log(e.message)
                
            #print info
        
        else:
            self.log('Uploading file %s in %s' % (drive_path, drive_dir))
            if dry_run:
                return
            
            try:
                info = api.upload(self.drive, local_file, parent.id)
            except api.errors.HttpError as e:
                self.log('Cannot upload file %s' % local_file, 'warning')
                self.log(e.message)
                return
            
            newdir = GDriveFile(info, parent)
            parent.add_child(newdir)
            
            #print info
    
    def delete_file(self, remote_file_path, dry_run=False):
        """
        Delete a file (move to trash)
        """
        # Get hold of 
        item = self.root.get_child(remote_file_path)
        parent = item.parent
        
        self.log('Deleting file %s' % item.path)
        
        if dry_run:
            return
        
        try:
            _info = api.delete(self.drive, file_id=item.id)
        except api.errors.HttpError as e:
            self.log('Cannot delete %s' % item.path, 'warning')
            self.log(str(e))
            return
        
        parent.unlink_child(item)
    
    def get_differences(self, drive_dir, local_dir, skip_dot_files_and_dirs=False):
        """
        Get the difference between local and remote directories
        
        Returns a list of GDriveSyncDifference objects
        """
        self.log('\nGetting differences between')
        self.log(' local directory: %s' % local_dir)
        self.log(' drive directory: %s' % drive_dir)
        
        local_dir = os.path.expanduser(local_dir)
        if not os.path.isdir(local_dir):
            raise GDriveSyncError('Local directory %s is not found' % os.path.abspath(local_dir))
        
        # List of differences that we find
        differences = []
        
        # Cache of local files and folders of class LocalItem 
        local_data = {}
        
        ################################################################################
        # Get the Google Drive directory 
        try:
            drive_dir_obj = self.root.get_child(drive_dir)
        except KeyError:
            # Top level directory does not exist
            #  -> Mark top level directory as missing 
            differences.append(GDriveSyncDifference(GDriveSyncDifference.ONLY_LOCAL,
                                                    local_file=os.path.abspath(local_dir)))
            #  -> Mark everything under the top level directory as missing
            for root, dirs, files in os.walk(unicode(local_dir)):
                if skip_dot_files_and_dirs:
                    # Skip hidden directories
                    for dirname in list(dirs):
                        if dirname[0] == '.':
                            dirs.remove(dirname)
                
                for item in files + dirs:
                    if skip_dot_files_and_dirs and item[0] == '.':
                        # Skip hidden files 
                        continue
                    differences.append(GDriveSyncDifference(GDriveSyncDifference.ONLY_LOCAL,
                                                            local_file=os.path.join(root, item)))
            return differences
        
        if not drive_dir_obj.is_dir:
            raise GDriveSyncError('Requested path %r is not a directory on the Drive' % drive_dir)
        
        ################################################################################
        # Find changes between remote and local
        stack = [(child, [child.name]) for child in drive_dir_obj.children.itervalues()]
        while stack:
            item, pth = stack.pop()
            
            if item.is_dir:
                stack.extend((child, pth + [child.name]) for child in item.children.itervalues())
            
            # Check if the local item is present
            pth_loc = os.path.join(local_dir, *pth)
            if pth_loc in local_data:
                local = local_data[pth_loc]
            elif os.path.isfile(pth_loc):
                local = local_data[pth_loc] = LocalItem(pth_loc, is_file=True)
            elif os.path.isdir(pth_loc):
                local = local_data[pth_loc] = LocalItem(pth_loc, is_dir=True)
            else:
                differences.append(GDriveSyncDifference(GDriveSyncDifference.ONLY_REMOTE, remote_file=item.path))
                continue
            local_data[pth_loc] = local
            
            # Check that local and remote are either both files or both directories 
            if item.is_dir != local.is_dir:
                differences.append(GDriveSyncDifference(GDriveSyncDifference.FILE_DIRECTORY_MISMATCH,
                                                        remote_file=item.path,
                                                        local_file=pth_loc))
                continue
            
            # If the item is a directory it is considered to be equal on remote and local
            if item.is_dir:
                continue
            # If the item has been modified locally after previous upload then files are different
            elif local.modified > item.modified:
                differences.append(GDriveSyncDifference(GDriveSyncDifference.NEWER_LOCAL,
                                                        remote_file=item.path,
                                                        local_file=pth_loc))
                continue
            # If the file sizes differ then the files are different (obviously)
            elif local.file_size != item.file_size:
                print 'Different', local.path, local.file_size, item.file_size
                differences.append(GDriveSyncDifference(GDriveSyncDifference.FILES_ARE_DIFFERENT,
                                                        remote_file=item.path,
                                                        local_file=pth_loc))
                continue
        
        ################################################################################
        # Find items on local disk that are not present on the remote
        for root, dirs, files in os.walk(unicode(local_dir)):
            if skip_dot_files_and_dirs:
                # Skip hidden directories
                for dirname in list(dirs):
                    if dirname[0] == '.':
                        dirs.remove(dirname)
            
            for item in files + dirs:
                if skip_dot_files_and_dirs and item[0] == '.':
                    # Skip hidden files 
                    continue
                
                pth_loc = os.path.join(root, item)
                
                # Have we already dealt with this above? In that case it is should be OK
                if pth_loc in local_data:
                    continue
                
                # File or directory is not on Drive
                differences.append(GDriveSyncDifference(GDriveSyncDifference.ONLY_LOCAL, local_file=pth_loc))
        
        return differences
    
    def log(self, message, flag='info'):
        """
        By default messages are printed to stdin if verbose=True
        """
        prefix = ''
        if flag == 'warning':
            prefix = 'WARNING: '
            self.logged_warnings.append(message)
        elif flag == 'error':
            prefix = 'ERROR: '
            self.logged_errors.append(message)
        if self.verbose:
            print prefix + message
    