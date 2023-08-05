import os.path, pipes, getpass, logging, pickle, tempfile, shutil, warnings
import util

class Repository(object):
    def __init__(self, path='/srv/bishop/'):
        self.path = path
        self.keyfile = None
        self.password = None
        if self.path[0] == '/' and not os.path.exists(self.path):
            os.makedirs(self.path)

        if not self.path.endswith('/'):
            self.path += '/'

    @property
    def all_roles(self):
        try:
            return [os.path.basename(path) for path in self.cmd('find {root}* -prune -type d').strip().splitlines()]
        except Exception, e:
            if 'No such file' in str(e):
                return []
            else:
                raise

    @property
    def hostname(self):
        '''return the host name part of repository location - or localhost for a local filesystem'''
        if self.path[0] == '/':
            return 'localhost'

        (server, path) = self.path.split(':', 1)
        if '@' in server:
            (user, server) = server.split('@', 1)

        return server

    @property
    def cluster(self):
        '''Grab the list of connected hosts and when they've installed, then return them split by roles'''
        warnings.simplefilter('ignore')
        path = os.tempnam() + '/'
        warnings.resetwarnings()
        os.mkdir(path)

        self.copy_down('.hosts.*', path)
        
        cluster = {}
        for role in self.all_roles:
            cluster[role] = {}
        
        for host_path in os.listdir(path):
            host_name = host_path[7:]
            saved = pickle.load(open(os.path.join(path, host_path), 'r'))
            for role in saved['roles']:
                if role in cluster:
                    cluster[role][host_name] = saved

            for role in saved['mixed_roles']:
                if role in cluster:
                    cluster[role]['(%s)' % host_name] = saved

        shutil.rmtree(path, True)
        return cluster

    @property
    def sync_disabled(self):
        '''Return False if the sync commands are enabled, or the message to show to users if they are disabled'''
        try:
            return self.cmd('cat {root}.bishop.nosync')
        except:
            return False

    def copy_down(self, from_path, to_path, include=None):
        '''Sync files from the repository to the given local filesystem path'''
        return self.copy(os.path.join(self.path, from_path), to_path, include)

    def copy_up(self, from_path, to_path, include=None):
        '''Sync files from the local filesystem to the repository'''
        return self.copy(from_path, os.path.join(self.path, to_path), include)

    def copy(self, from_path, to_path, include=None):
        '''Copy things around using rsync - presume that all paths are absolute or cwd-relative'''

        keyfile_auth = ''
        include_args = ''

        if self.keyfile is not None:
            keyfile_auth = '-e "ssh -i %s"' % pipes.quote(self.keyfile)

        if include is not None:
            include_args = ' '.join(['--include=%s' % pipes.quote(include_pat) for include_pat in include] + ['--exclude=*'])
        
        cmd = 'rsync -rlptDz --delete %s %s %s %s' % (keyfile_auth, include_args, from_path, to_path)
        
        if self.password is not None:
            return self.copy_passwd(cmd)
        else:
            return util.shell(cmd)

    def copy_passwd(self, cmd):
        '''Copy things around using rsync and pexpect to handle the tty-based password inputs'''
        import pexpect
        logging.debug(cmd)
        child = pexpect.spawn(cmd)
        child.expect('password: ')
        child.sendline(self.password)
        child.expect(pexpect.EOF)
        child.close()

    def delete_role(self, role):
        '''Delete a role from the repo'''
        return self.cmd('rm -rf {root}%s' % role)
    
    def disable_sync(self, msg=None):
        '''Disable the sync and sync-down commands, instead showing a message to the user'''
        f = tempfile.NamedTemporaryFile()
        content = 'The sync commands have been disabled on this repository.\n'
        if msg is not None:
            content += '\n' + msg + '\n'

        f.write(content)
        f.flush()
        os.chmod(f.name, 0644)
        self.copy_up(f.name, '.bishop.nosync')
        f.close()

    def enable_sync(self):
        '''Enable the sync and sync-down commands if they're disabled'''
        return self.cmd('rm -f {root}.bishop.nosync')

    def cmd(self, cmd):
        '''Execute an SSH command on the repo server'''
        if self.path[0] == '/':
            cmd = cmd.replace('{root}', self.path)
            return util.shell(cmd)

        if self.password is not None:
            return self.cmd_passwd(cmd)
        
        (server, path) = self.path.split(':', 1)
        cmd = cmd.replace('{root}', path)

        keyfile_auth = ''
        if self.keyfile is not None:
            keyfile_auth = '-i %s' % pipes.quote(self.keyfile)

        cmd = 'ssh %s %s %s' % (keyfile_auth, server, pipes.quote(cmd))
        return util.shell(cmd)

    def cmd_passwd(self, cmd):
        '''Execute an SSH command on the repo server, using pexpect to supply a password'''
        import pexpect
        
        (server, path) = self.path.split(':', 1)
        cmd = cmd.replace('{root}', path)

        cmd = 'ssh %s %s' % (server, pipes.quote(cmd))
        logging.debug(cmd)
        child = pexpect.spawn(cmd)
        child.expect('password: ')
        child.sendline(self.password)
        out = pexpect.read()
        child.close()
        return out

    def ask_password(self):
        '''Ask for the remote password without showing it in the tty'''
        self.password = getpass.getpass()

    def save(self, host):
        '''Maintain a log of hosts and roles so we can have a sense of the "cluster"'''
        to_save = ['roles', 'last_install', 'ip', 'mixed_roles']
        saved = {}
        for field in to_save:
            saved[field] = getattr(host, field)

        f = tempfile.NamedTemporaryFile()
        pickle.dump(saved, f)
        f.flush()
        os.chmod(f.name, 0644)
        self.copy_up(f.name, '.hosts.%s' % host.name)
        f.close()

    def __str__(self):
        return self.path
