"""
Command line module for gdrive_sync
"""
from __future__ import absolute_import
import sys, argparse, time, logging
from gdrive_sync import GDriveSync, GDriveSyncError, GDriveSyncDifference as Difference

hdlr = logging.StreamHandler()
hdlr.setLevel(logging.WARNING)
logging.getLogger().addHandler(hdlr)

def update(args):
    """
    Update the database of changes with whatever has changed since the last update
    """
    gds = GDriveSync(verbose=True)
    gds.connect()
    gds.update()
    
    log_problems(gds)

def print_differences(args):
    """
    Print changes between local directory and what is on the Drive
    """
    t1 = time.time()
    print '\n----------------- RUNNING -------------------'
    gds = GDriveSync(verbose=True)
    try:
        gds.build_file_tree()
        differences = gds.get_differences(args.remote_dir, args.local_dir)
    except GDriveSyncError as e:
        print '\nERROR:\n    %s' % e.message
        sys.exit(1)
    print 'DONE in %.1f seconds' % (time.time() - t1)
    print '-------------- END OF RUNNING -----------------'
    
    print '\n---------------- DIFFERENCES ------------------'
    for diff in differences:
        if diff.reason == Difference.ONLY_LOCAL:
            print 'Only on local disk: %s' % diff.local_file
        elif diff.reason == Difference.ONLY_REMOTE:
            print 'Only on Google Drive: %s' % diff.remote_file
        elif diff.reason == Difference.NEWER_LOCAL:
            print 'Newer on local disk: %s' % diff.local_file
        elif diff.reason == Difference.FILES_ARE_DIFFERENT:
            print 'Files are different: %s, %s' % (diff.remote_file, diff.local_file)
        else:
            print '\nERROR:\n    Unknown difference type %s' % diff.reason
            sys.exit(1)
    print '-------------- END OF DIFFERENCES --------------'
    
    log_problems(gds)
    
    return gds, differences

def sync_up(args):
    """
    Upload missing files and directories to google Drive
    """
    # First, update the database
    update(args)
    
    # Then, print the differences between local and remote directory
    gds, differences = print_differences(args)
    
    allow_delete = args.delete
    
    if not differences:
        print 'No differences found!'
        return
    
    print '\n-------------------- ASK ----------------------'
    print '\nDo you want to synchronize from local disk to Google Drive?'
    print 'Local directory:       ', args.local_dir
    print 'Google Drive directory:', args.remote_dir
    if allow_delete:
        print 'The program will delete files on Google Drive that are not present locally!'
    else:
        print 'The program will NOT delete files on Google Drive that are not present locally'
    if not (args.yes or args.dry_run):
        yN = raw_input('Continue [y/N]? ')
        if yN.strip().lower() not in ('y', 'yes'):
            print 'Will do nothing'
            return
    
    print '\n-------------------- SYNC ---------------------'
    
    # Connect to the Drive
    gds.connect()
    
    for diff in differences:
        print
        if diff.reason == Difference.ONLY_LOCAL:
            gds.upload_file(args.remote_dir, args.local_dir, diff.local_file, dry_run=args.dry_run)
        elif diff.reason == Difference.ONLY_REMOTE:
            if allow_delete:
                gds.delete_file(diff.remote_file, dry_run=args.dry_run)
        elif diff.reason == Difference.NEWER_LOCAL:
            gds.upload_file(args.remote_dir, args.local_dir, diff.local_file, update=True, dry_run=args.dry_run)
        elif diff.reason == Difference.FILES_ARE_DIFFERENT:
            print 'Files are different: %s, %s (doing nothing)' % (diff.remote_file, diff.local_file)
        else:
            print '\nERROR:\n    Unknown difference type %s' % diff.reason
            sys.exit(1)
    
    print '-------------------- DONE ---------------------'
    log_problems(gds)
    
def log_problems(gds):
    print '\n------------------- STATUS ---------------------'
    print 'Finished with %d warnings and %d errors' % (len(gds.logged_warnings), len(gds.logged_errors))
    for msg in gds.logged_warnings:
        print 'WARNING: %s' % msg
    for msg in gds.logged_errors:
        print 'ERROR: %s' % msg
    print '---------------- END OF STATUS ----------------'

def command_line_interface():
    # create the top-level parser
    parser = argparse.ArgumentParser(description='Synchronize directories with Google Drive')
    subparsers = parser.add_subparsers()
    
    parser_update = subparsers.add_parser('update')
    parser_update.set_defaults(func=update)
    
    parser_diff = subparsers.add_parser('diff')
    parser_diff.set_defaults(func=print_differences)
    parser_diff.add_argument('remote_dir', default='/', nargs='?', help='The directory on Google Drive')
    parser_diff.add_argument('local_dir', default='.', nargs='?', help='The local directory')
    
    parser_diff = subparsers.add_parser('sync-up')
    parser_diff.set_defaults(func=sync_up)
    parser_diff.add_argument('remote_dir', default='/', nargs='?', help='The directory on Google Drive')
    parser_diff.add_argument('local_dir', default='.', nargs='?', help='The local directory')
    parser_diff.add_argument('-d', '--dry-run', action='store_true', dest='dry_run',
                             help='print what will be done, but do not do it')
    parser_diff.add_argument('-y', action='store_true', dest='yes',
                             help='do not ask if you want to sync, just do it')
    parser_diff.add_argument('-x', '--delete', action='store_true', dest='delete',
                             help='allow deleting files (default off)')
    
    # Parse the arguments and call whatever function was selected
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    command_line_interface()
