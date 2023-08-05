import subprocess, logging, os.path, sys
import error

# Template vars will be pulled from /etc/bishop-vars.json as a JSON document, but of course a JSON library needs to be available
vars_enabled = False
vars_path = '/etc/bishop-vars.json'
try:
    import json
    vars_enabled = True
except:
    try:
        import simplejson as json
        vars_enabled = True
    except:
        pass

def shell(args):
    '''Wrapper around subprocess calls with a sensible default - return stdout as string.  On a non-zero error code, throw an exception with stderr'''
    logging.debug('shell: %s' % args)
    p = subprocess.Popen(args, shell=isinstance(args, basestring), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate()
    retcode = p.wait()
    if retcode:
        raise error.CalledProcessError(retcode, args, stderr)

    return stdout

def uncomment_lines(body):
    '''Take a body string and return a list of lines with comments and empty lines stripped out'''
    def _uncomment_line(line):
        if '#' in line:
            return line[:line.index('#')].strip()
        return line.strip()

    return [_uncomment_line(line) for line in body.splitlines() if _uncomment_line(line) != '']

def chown_makedirs(path):
    '''Perform the same task as os.makedirs, but pull the uid and gid from the parent dir instead of the running process'''
    path = os.path.realpath(path)
    dirpath = '/'
    for part in path.strip('/').split('/'):
        dirpath = os.path.join(dirpath, part)
        if os.path.isdir(dirpath):
            continue
        if os.path.exists(dirpath):
            raise ValueError('%s exists but is not a directory' % dirpath)

        os.mkdir(dirpath)
        st = os.stat(os.path.dirname(dirpath))
        os.chown(dirpath, st.st_uid, st.st_gid)

_tplvars = None
def get_tplvars():
    global _tplvars

    if _tplvars is not None:
        return _tplvars
    if not os.path.exists(vars_path):
        _tplvars = {}
        return _tplvars
    if not vars_enabled:
        raise Exception('Bishop vars file requires Python 2.6+ or the simplejson library installed')
    _tplvars = json.load(open(vars_path, 'r'))
    return _tplvars

def validate_repopath(path):
    '''Test if a given path looks like a repo (all subfolders have files, templates, template-includes, or other bishop-isms)'''
    expect_dirs = ['files', 'templates', 'template-includes'] # at least one of these needs to appear for a role to be considered valid
    expect_files = ['packages', 'preinst', 'postinst', 'prepackage', 'mixins']

    for role in [role for role in os.listdir(path) if os.path.isdir(os.path.join(path, role)) and not role.startswith('.')]:
        role_path = os.path.join(path, role)
        good_role = False

        for d in expect_dirs:
            if os.path.isdir(os.path.join(role_path, d)):
                good_role = True

        for f in expect_files:
            if os.path.isfile(os.path.join(role_path, f)):
                good_role = True

        if not good_role:
            raise Exception('This isn\'t a bishop repo.  Are you trying to sync from some random directory?')
    
    return True

def get_repopath():
    '''Search the ancestors of the current working directory for a local bishop repo copy.  If we can't find one, the current working directory is the root of the copy and mark it.'''
    path = os.getcwd()
    while not os.path.exists(os.path.join(path, '.bishop.repo')) and path != '/':
        path = os.path.dirname(path)

    if path == '/':
        path = os.getcwd()

    mark_path = os.path.join(path, '.bishop.repo')
    if not os.path.exists(mark_path):
        validate_repopath(path)
        f = open(mark_path, 'w')
        f.write('1')
        f.close()

    return path

def cpu_count():
    '''Return the number of active CPU cores on this machine'''
    if 'bsd' in sys.platform or sys.platform == 'darwin':
        try:
            p = os.popen('sysctl -n hw.ncpu')
            return int(p.read())
        except ValueError:
            return 0
    else:
        try:
            return os.sysconf('SC_NPROCESSORS_ONLN')
        except (ValueError, OSError, AttributeError):
            return 0

def system_memory():
    '''Return the amount of RAM on the system in bytes'''
    return os.sysconf('SC_PHYS_PAGES') * os.sysconf('SC_PAGE_SIZE')
