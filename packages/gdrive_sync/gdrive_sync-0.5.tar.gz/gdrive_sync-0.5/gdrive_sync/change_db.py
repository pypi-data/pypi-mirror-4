import os
import cPickle as pickle
import dateutil.parser
from collections import defaultdict

from . import gdrive_communication as api

class ChangeDB(object):
    def __init__(self, filename, logger=None):
        """
        This class stores the Google Drive file changes. The format of the
        changes is identical with the dictionaries returned by the Google
        Python API code for Google Drive
        """
        self.filename = filename
        if logger is None:
            self.logger = lambda msg, flag=None: None
        else:
            self.logger = logger
        
    @property
    def changes(self):
        return self.database['changes']
    
    @property
    def max_change_id(self):
        return self.database['max_change_id']
    
    def add_change(self, change):
        """
        Add change to the database
        """
        cid = int(change['id'])
        assert cid not in self.database['changes']
        assert cid > self.database['max_change_id']
         
        self.database['max_change_id'] = cid
        self.database['changes'][cid] = change
    
    def read(self):
        """
        Load change database from disk
        """
        if os.path.isfile(self.filename):
            # Read database from file
            with open(self.filename, 'rb') as f:
                self.database = pickle.load(f)
        else:
            self.database = {'max_change_id': 0, 'changes': {}}
            self.logger('Creating new change set database')
            # Check that we can write to the database file
            self.write()
        
        self.logger('Loaded changes database containing %d changes. Last change id is %d' % (len(self.changes), self.max_change_id))
    
    def get_file_tree(self, include_trashed=False):
        """
        Replay the stored changes in the database to create a local
        representation of the current state of the remote Drive
        """
        changes = self.changes
        id_to_obj_map = {}
        deleted = set()
        if not changes:
            return GDriveDirectory(None, None)
        
        keys = sorted(changes.keys())
        sorted_changes = [self.changes[cid] for cid in keys]
        
        roots = []
        
        for c in sorted_changes:
            fid = c['fileId']
            if c.get('deleted', False):
                if fid in id_to_obj_map:
                    obj = id_to_obj_map[fid]
                    obj.delete()
                    del id_to_obj_map[fid]
                else:
                    pass
                    #print 'Object to delete is not in map', c
                deleted.add(fid)
                continue
                
            f = c['file']
            assert f['id'] == fid
            
            assert len(f['parents']) == 1
            parent_id = f['parents'][0]['id']
            if parent_id in id_to_obj_map:
                parent = id_to_obj_map[parent_id]
            else:
                parent = GDriveDirectory({'id': parent_id}, None)
                id_to_obj_map[parent_id] = parent
                #print 'Found unrooted object %s' % f['title'], fid
                roots.append(parent)
            
            if fid in id_to_obj_map:
                obj = id_to_obj_map[fid]
                if obj.is_root:
                    #print 'Rooting object %s' % f['title'], fid
                    roots.remove(obj)
                obj.update(f, parent)
            else:
                if f['mimeType'] == api.MIME_DIRECTORY:
                    obj = GDriveDirectory(f, parent)
                else:
                    obj = GDriveFile(f, parent)
                parent.add_child(obj)
                id_to_obj_map[fid] = obj
        
        roots = [s for s in roots if s.id not in deleted]
        
        # Check that nothing major is wrong
        assert len(roots) == 1
        root = roots[0]
        assert root.is_root
        assert root.parent is None
        
        # Remove trashed before verify - it might be duplicates where one is trashed and the other not
        if not include_trashed:
            root.remove_all_trashed()
        
        # Check that everything is OK with the constructed file tree
        root.verify(self.logger)
        
        return root
    
    def write(self):
        """
        Save change database to disk
        """
        with open(self.filename, 'wb') as f:
            pickle.dump(self.database, f, protocol=pickle.HIGHEST_PROTOCOL)
        self.logger('Saved changes database containing %d changes. Last change id is %d' % (len(self.changes), self.max_change_id))
    
    def __enter__(self):
        """
        Allow the database to be used as a context manager
        """
        self.read()
        return self
    
    def __exit__(self, *argv):
        """
        Allow the database to be used as a context manager
        make sure that the database is saved to disk
        """
        self.write()
        if argv[0] is not None:
            self.logger('Emergency saved changes database due to exception')

class GDriveFile(object):
    is_file = True
    is_dir = False
    is_deleted = False
    
    def __init__(self, info, parent):
        self.parent = parent
        self.info = info
        self.is_root = self.parent is None
    
    @property
    def id(self):
        return self.info['id']
    
    @property
    def name(self):
        if self.is_root:
            return '/'
        
        orig = self.info.get('originalFilename', None)
        title = self.info.get('title', None)
        ext = self.info.get('fileExtension', None)
        
        if orig:
            return orig
        elif ext and title.endswith(ext):
            return title
        elif ext:
            return '%s.%s' % (title, ext)
        else:
            return title
    
    @property
    def path(self):
        "The full path to this drive item"
        if self.is_root:
            return '/'
        pth = self.name
        parent = self.parent
        while not parent.is_root:
            pth = parent.name + '/' + pth
            parent = parent.parent
        return '/' + pth
    
    @property
    def modified(self):
        isotime = self.info['modifiedDate'] # Format: 2013-01-16T15:07:34.915Z
        return dateutil.parser.parse(isotime)
    
    @property
    def file_size(self):
        size = self.info['fileSize']
        return int(size)
    
    @property
    def is_trashed(self):
        return self.info['labels']['trashed']
    
    def delete(self):
        if self.parent is not None:
            self.parent.unlink_child(self)
        self.is_deleted = True
    
    def update(self, new_info, new_parent):
        # Swap parent if necessary
        assert len(new_info['parents']) == 1
        new_parent_id = new_info['parents'][0]['id']
        assert new_parent.id == new_parent_id
        
        if self.is_root:
            assert 'parents' not in self.info
            assert self.parent is None
            current_parent_id = None
        else:
            assert len(self.info['parents']) == 1
            current_parent_id = self.info['parents'][0]['id']
            assert self.parent.id == current_parent_id
        
        if new_parent_id != current_parent_id:
            self._swap_parent(new_parent)
        
        # Update information
        self.is_root = False # root object will never be updated
        self.info = new_info
    
    def _swap_parent(self, new_parent):
        if self.parent is not None:
            self.parent.unlink_child(self)
            
        if new_parent is not None:
            new_parent.add_child(self)
            self.is_root = False
        else:
            self.is_root = True
        self.parent = new_parent
    
    def verify(self, logger):
        assert self.info is not None
        assert not self.is_deleted
        if self.is_root:
            assert self.is_dir and not self.is_file
            assert self.parent is None
        else:
            assert self.parent is not None
            assert len(self.info['parents']) == 1
            assert self.id in self.parent.children
            
            if not self.parent.is_root:
                assert self.parent.id == self.info['parents'][0]['id']
        
            if self.is_dir:
                assert not self.is_file
                assert self.info['mimeType'] == api.MIME_DIRECTORY
            else:
                assert self.is_file
                assert self.info['mimeType'] != api.MIME_DIRECTORY

class GDriveDirectory(GDriveFile):
    is_file = False
    is_dir = True
    
    def __init__(self, info, parent):
        super(GDriveDirectory, self).__init__(info, parent)
        self.children = {}
    
    def get_children(self):
        return self.children.values()            
            
    def add_child(self, child):
        self.children[child.info['id']] = child
    
    def unlink_child(self, child):
        del self.children[child.info['id']]
    
    def get_child(self, path):
        """
        Get a child or a grand child, great grand child etc. The path
        is interpreted in the Unix manner with separator '/'
        """
        if '/' in path:
            # This is a path to a sub-directory
            pth_elems = path.split('/')
            if pth_elems[0] == '':
                assert self.is_root
                pth_elems = pth_elems[1:]
            
            elem = self
            for name in pth_elems:
                if not elem.is_dir:
                    raise KeyError('Item "%s" is a file, not a directory' % elem.path)
                if name == '':
                    continue
                elem = elem[name]
            return elem
        else:
            # This is a name to a item in this directory
            for c in self.children.itervalues():
                if c.name == path:
                    return c
            raise KeyError('Item "%s" in "%s" not found on Drive' % (path, self.path))
    __getitem__ = get_child
    
    def has_file(self, filename):
        for c in self.children.itervalues():
            if c.name == filename:
                return c.is_file
        return False
    
    def has_dir(self, filename):
        for c in self.children.itervalues():
            if c.name == filename:
                return c.is_dir
        return False
    
    def remove_all_trashed(self):
        stack = self.children.values()
        while stack:
            item = stack.pop()
            if item.is_trashed:
                item.delete()
            if item.is_dir:
                stack.extend(item.children.itervalues())
    
    def verify(self, logger):
        super(GDriveDirectory, self).verify(logger)        
        names = defaultdict(list)
        for cid, c in self.children.iteritems():
            assert cid == c.info['id']
            names[c.name].append(c)
            
            if c.parent is not self:
                print 'Item "%s" claims "%s" as its parent, but is found in "%s"' % (c.name, c.parent.path, self.path)
            
            c.verify(logger)
        
        for name, children in names.iteritems():
            if len(children) == 1:
                continue
            logger('There are %d items called "%s" on Drive in "%s"' % (len(children), name, self.path), 'warning')
