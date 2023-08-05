import os.path, sys

# modified from:
# http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
# who attributes it to dead link by 'Fred Cirera'
def humanize_sizeof(num):
    '''Provides mostly-human-readable file sizes. Some sizes
    result in sub-optimal representations, like one byte shy of
    a megabyte yields 1024KB. We persevere.'''
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def is_file(file_name):
    if os.path.isfile(file_name):
        return True
    return False

def get_size(file_name):
    ''' bytes, -1 if error '''
    if not os.path.isfile(file_name):
        return -1
    return os.path.getsize(file_name)

def get_humanized_size(file_name):
    ''' returns a string describing file size '''
    if not os.path.isfile(file_name):
        return None
    return humanize_sizeof(os.path.getsize(file_name))

def get_file_summary(file_name, max_size = 5000, append_total = False):
    ''' max_size of None means get all '''
    if not os.path.isfile(file_name):
        return "[Couldn't find file]"
    fin = open(file_name)
    contents = None
    if not max_size or get_size(file_name) < max_size:
        contents = fin.read()
    else:
        contents = fin.read(max_size)
    fin.close()
    if append_total and get_size(file_name) > max_size:
        contents += "\n... of {0}".format(get_humanized_size(file_name))
    return contents

def remove_shallow_dir(path):
    ''' Doesn't do subdirectories, but then we shouldn't have any. '''
    for the_file in os.listdir(path):
        file_path = os.path.join(path, the_file)
        try:
            os.unlink(file_path)
        except Exception, e:
            print e
    try:
        os.rmdir(path)
    except Exception, e:
        print e

def assert_no_tilde(path):
    '''Yes, I know that there are better ways to do this.'''
    if path and "~" in path:
        sys.stderr.write("Please don't use ~, resolving it is hard: %s\n" % path)
        sys.exit(1)

# NOTE: the discovery method for which executions to delete piggybacks
# on the very specific date format. The date is designed to be sortable
# and human readable.
def clear_old_dirs(path, max_keep):
    all_dirs = os.listdir(path)
    if max_keep > len(all_dirs):
        return
    # unexpected: osx and centos-linux reverse default sort, so have to
    # do it explicitly
    all_dirs.sort()
    all_dirs.reverse()
    dirs_to_delete = all_dirs[max_keep:]
    for one_del in dirs_to_delete:
        remove_shallow_dir(os.path.join(path, one_del))
