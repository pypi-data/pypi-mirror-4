import pickle, os.path, fcntl, time, shutil, logging, platform, xmlrpclib, sys
import role, package, util, error
try:
    from hashlib import sha1 as sha
except ImportError:
    from sha import new as sha

class Local(object):
    def __init__(self, path='/var/lib/bishop/'):
        self.path = path
        if not os.path.isdir(self.path):
            os.makedirs(self.path, 0777)
        self.repo = None
        self.last_install = 0
        self.install_locked = False
        self.roles = []
        self._roles = {}
        self._owned = {}
        self._locked = False
        self.load()

    def __del__(self):
        if self._locked: self.unlock()

    @property
    def build_path(self):
        return os.path.join(self.path, '.build')

    @property
    def name(self):
        return platform.node()

    @property
    def ip(self):
        '''Return the IP address that this host uses to connect to the repository'''
        if self.repo is None:
            return None

        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((self.repo.hostname, 0))
        return s.getsockname()[0]

    @property
    def mixed_roles(self):
        '''Return the list of roles that this host implicitly installs via mixins from its explicit roles'''
        mixins = set()

        def recurse_mixins(role):
            for mixin in self.role(role).mixins:
                if not mixin in mixins:
                    mixins.add(mixin)
                    recurse_mixins(mixin)

        for role in self.roles:
            recurse_mixins(role)

        [mixins.discard(role) for role in self.roles]
        return list(mixins)

    def load(self):
        '''Load the saved host data from the serialized snapshot file'''
        save_path = os.path.join(self.path, '.save')
        if not os.path.exists(save_path):
            return

        saved = pickle.load(open(save_path, 'r'))
        for k, v in saved.iteritems():
            setattr(self, k, v)

    def save(self):
        '''Save this host's current options to a serialized snapshot file'''
        unlock = self.lock()
        
        to_save = ['repo', 'roles', 'last_install', 'install_locked']
        saved = {}
        for attr in to_save:
            saved[attr] = getattr(self, attr)

        save_path = os.path.join(self.path, '.save')
        f = open(save_path, 'w')
        pickle.dump(saved, f)
        f.close()

        if self.repo is not None:
            self.repo.save(self)

        if unlock: self.unlock()

    def mirror(self, roles=None, done=None, repo_roles=None):
        '''Find the roles given in this host's repository and sync changes down to the host cache'''
        if repo_roles is None: repo_roles = self.repo.all_roles
        
        if roles is None:
            self.roles = [role for role in self.roles if role in repo_roles]
            roles = self.roles
        elif len(roles) > 0:
            roles = [role for role in roles if role in repo_roles]

        if len(roles) == 0:
            return
        
        # Accumulate the finished roles so we don't double-sync or fail on circular mixins
        if done is None:
            done = {}

        mirror_roles = [role for role in roles if role not in done]
        if len(mirror_roles) == 0:
            return

        self.repo.copy_down('', self.path, ['/' + role + '/' for role in mirror_roles] + ['/' + role + '/**' for role in mirror_roles])
        
        mixin_roles = []
        for role in mirror_roles:
            done[role] = True
            mixin_roles.extend([mix for mix in self.role(role).mixins if mix not in done and mix not in mixin_roles])

        self.mirror(mixin_roles, done, repo_roles)
    
    def role(self, name):
        '''Given a name, make sure we have a Role instance, cached by name per host'''
        if isinstance(name, role.Role):
            return name

        if name not in self._roles:
            self._roles[name] = role.Role(self, name)

        return self._roles[name]

    def sync_down(self):
        '''Copy from the repository to the current working directory'''
        disabled = self.repo.sync_disabled
        if disabled:
            print disabled
            return
        path = util.get_repopath()
        repo_roles = self.repo.all_roles
        self.repo.copy_down('', path + '/', ['/' + role + '/' for role in repo_roles] + ['/' + role + '/**' for role in repo_roles])
        self.snapshot_wc(path)

    def sync_up(self):
        '''Copy from the current working directory up to the repository'''
        disabled = self.repo.sync_disabled
        if disabled:
            print disabled
            return
        path = util.get_repopath()
        roles = [role for role in os.listdir(path) if not role.startswith('.') and os.path.isdir(os.path.join(path, role))]
        
        snap_path = os.path.join(path, '.bishop.files')
        try:
            f = open(snap_path, 'r')
            prev_files = pickle.load(f)
            f.close()
        except:
            prev_files = {}

        for role in roles:
            changed, deleted = self.sync_changes(os.path.join(path, role), prev_files)
            
            if len(deleted) > 0:
                #Deletes cannot be rsynced, so just sync the whole changed role
                self.repo.copy_up(os.path.join(path, role) + '/', role + '/')
            else:
                for change_file in changed:
                    self.repo.copy_up(change_file, change_file[len(path) + 1:])

        # if we succeed in syncing up to the repo, remove any locks on remote install since local and remote are in sync
        if self.install_locked:
            self.install_locked = False
            self.save()

        self.snapshot_wc(path)

    def snapshot_wc(self, path):
        '''Take a snapshot of the files and their modification times so we can be more targetted in what we sync back up to the repo - some multi-user protection'''
        roles = [role for role in os.listdir(path) if not role.startswith('.') and os.path.isdir(os.path.join(path, role))]
        
        snapshot = {}
        for role in roles:
            for root, dirs, files in os.walk(os.path.join(path, role)):
                for fpath in files:
                    full_path = os.path.join(root, fpath)
                    snapshot[full_path] = os.stat(full_path).st_mtime

                for dpath in dirs:
                    full_path = os.path.join(root, dpath)
                    snapshot[full_path] = os.stat(full_path).st_mtime

                if len(files) == 0 and len(dirs) == 0 and root not in snapshot:
                    #Orphan directories should be snapshotted
                    snapshot[root] = os.stat(root).st_mtime
        
        snap_path = os.path.join(path, '.bishop.files')
        f = open(snap_path, 'w')
        pickle.dump(snapshot, f)
        f.close()
    
    def sync_changes(self, path, prev_files):
        '''Compare the current tree with the previous snapshot to get a list of changed files within a given role'''
        
        new_role = True
        found_files = []
        changed = []
        for root, dirs, files in os.walk(path):
            rel_root = root[len(path) - 1:]
            for fpath in files:
                full_path = os.path.join(root, fpath)
                found_files.append(full_path)
                if full_path not in prev_files:
                    changed.append(full_path)
                elif os.stat(full_path).st_mtime > prev_files[full_path]:
                    changed.append(full_path)
                    new_role = False
                else:
                    new_role = False

            for dpath in dirs:
                #All sub directories should be tracked
                full_path = os.path.join(root, dpath)
                found_files.append(full_path)
                if full_path not in prev_files:
                    changed.append(full_path + '/')
                else:
                    new_role = False

            if len(files) == 0 and len(dirs) == 0:
                #New orphan directories should also be tracked, if they aren't already tracked
                if root not in found_files:
                    found_files.append(root)
                    if '/' in rel_root and root not in prev_files:
                        changed.append(root + '/')
                
                if '/' not in rel_root:
                    new_role = False # Empty role directories are not new roles

        if new_role:
            return ([path + '/'], []) #new roles should just be synced all at once

        changed.sort(key=len)
        deleted = [p for p in prev_files.keys() if p.startswith(path) and p != path and p not in found_files] # also grab deleted files
        return (changed, deleted)


    def build(self, roles=None):
        '''Build a set of roles on this host, storing the snapshot of what will be done in $path/.build/'''
        unlock = self.lock()
        if roles is None:
            roles = self.roles
        
        self._owned = {}
        self._ready_packages = []
        self._ready_prepackage = {}
        shutil.rmtree(self.build_path, True)

        for role in roles:
            self.role(role).build()

        #For the sake of the build directory being a single, complete snapshot of what will be installed, serialize the package list to the metadata directory
        meta_path = os.path.join(self.build_path, '.bishop')
        try:
            os.makedirs(os.path.join(meta_path, '.prepackage'))
        except OSError:
            pass
        
        for name, script_path in self._ready_prepackage.items():
            os.symlink(os.path.abspath(script_path), os.path.join(meta_path, '.prepackage', name))

        open(os.path.join(meta_path, 'packages'), 'w').write('\n'.join(self._ready_packages))
        if unlock: self.unlock()

    def ready(self, build_path, role):
        '''Mark a built path as owned by the role that built it so we can detect and flag better errors on conflicts between roles'''
        self._owned[build_path] = role

    def ready_package(self, name):
        '''Add a package to the list of packages to be installed'''
        if not name in self._ready_packages:
            self._ready_packages.append(name)

    def ready_prepackage(self, path, name):
        '''Add a prepackage script to be run before a given package is installed'''
        self._ready_prepackage[name] = path

    def install(self, roles=None, save=True, path='/', local=False):
        '''Build the given roles, then install the build on the local host'''
        if self.install_locked and not local:
            raise Exception('install cancelled - local host is locked for testing')

        unlock = self.lock()
        if roles is None:
            roles = self.roles
        elif save:
            self.roles = list(set(self.roles).union(set(roles)))
        # Roles should be added general-to-specific, but installed specific-to-general
        roles = roles.reverse()

        if self.repo is not None:
            self.mirror()
        self.build(roles)

        change_packages = self.get_new_packages()
        self.run_prepackages(change_packages)
        self.install_packages(change_packages)
        
        change_files = self.get_changes(path)
        self.run_preinstalls(change_files)
        [self.install_file(file, path) for file in change_files]
        self.run_postinstalls(change_files)
        
        self.last_install = time.time()
        self.save()
        if unlock: self.unlock()

    def uninstall(self, roles):
        '''Remove a set of roles from the roles this host checks'''
        unlock = self.lock()
        self.roles = list(set(self.roles).difference(set(roles)))
        self.save()
        if unlock: self.unlock()

    def get_new_packages(self):
        '''Return a list of only those packages that have not already been installed'''
        packager = package.Package()
        already_installed = packager.list()
        return [name for name in self._ready_packages if name not in already_installed]
        
    def run_prepackages(self, deps):
        '''Gather a unique list of the prepackage script to run based on what packages still need to be installed, and run them'''
        prepackages = {}
        for dep in deps:
            meta_path = os.path.join(self.build_path, '.bishop', '.prepackage', dep)
            if os.path.exists(meta_path):
                script_path = os.readlink(meta_path)
                if script_path in prepackages:
                    prepackages[script_path].append(dep)
                else:
                    prepackages[script_path] = [dep]

        for script_path, packages in prepackages.items():
            os.chmod(script_path, 0755)
            shell_args = [script_path]
            shell_args.extend(packages)
            logging.info('prepackage script %s' % script_path)
            util.shell(shell_args)

    def install_packages(self, deps):
        packager = package.Package()
        for dep in deps:
            logging.info('package install %s' % dep)
            packager.install(dep)

    def install_file(self, file_path, root):
        '''Atomically write the changed file to the given installation path'''
        install_path = os.path.join(root, file_path)
        if os.path.isfile(install_path):
            backup_path = os.path.join(self.path, '.backups', install_path[1:])
            if not os.path.isdir(os.path.dirname(backup_path)):
                try:
                    os.makedirs(os.path.dirname(backup_path))
                except:
                    pass
            shutil.copyfile(install_path, backup_path)
        build_path = os.path.join(self.build_path, file_path)
        build_path = os.path.abspath(build_path)

        #We assume that installations are allowed to mutate and move any files within the build directory
        orig_path = os.path.realpath(build_path)
        if os.path.isdir(orig_path) and not os.path.exists(install_path):
            util.chown_makedirs(install_path)
            return

        parent_dir = os.path.dirname(install_path)
        if not os.path.exists(parent_dir):
            util.chown_makedirs(parent_dir)

        # Pull the uid and gid from the parent directory
        st = os.stat(os.path.dirname(install_path))
        logging.info('install file %s (%s:%s)' % (install_path, st.st_uid, st.st_gid))

        if orig_path != build_path:
            # If the built file is a symlink, then copy the file so we can atomically move it to the install location without harming any non-build locations
            os.remove(build_path)
            shutil.copyfile(orig_path, build_path)
        shutil.move(build_path, install_path)
        os.chown(install_path, st.st_uid, st.st_gid)

    def run_preinstalls(self, changes):
        '''Scan the changed files looking for preinstall scripts and run them.  A preinstall script failure should terminate further installation.'''
        for script, files in self.pivot_meta(changes, 'preinstall').iteritems():
            os.chmod(script, 0755)
            shell_args = [script]
            shell_args.extend(['/%s' % name for name in files])
            logging.info('preinstall script %s' % script)
            util.shell(shell_args)

    def run_postinstalls(self, changes):
        '''Scan the changed files looking for postinstall scripts and run them.  A postinstall script failure should be logged but not halt running other postinstall scripts.'''
        postinstalls = self.pivot_meta(changes, 'postinstall')

        # Also include any postinstall scripts that have been modified since the last bishop run
        for role in [role for role in self._roles.itervalues() if role._built]:
            script_path = os.path.join(self.path, role.name, 'postinst')
            if os.path.exists(script_path) and script_path not in postinstalls and os.path.getmtime(script_path) > self.last_install:
                postinstalls[script_path] = []

        for script, files in postinstalls.iteritems():
            os.chmod(script, 0755)
            shell_args = [script]
            shell_args.extend(['/%s' % name for name in files])
            logging.info('postinstall script %s' % script)
            try:
                util.shell(shell_args)
            except error.CalledProcessError, e:
                logging.error(str(e))

    def pivot_meta(self, changes, name):
        '''Scan all files in changes for metadata files tagged with {name}, then return a dictionary of {name} paths as keys and lists of files referencing the metadata file as the value'''
        meta = {}
        for file in changes:
            meta_path = '%s-%s' % (os.path.join(self.build_path, '.bishop', file), name)
            if os.path.exists(meta_path):
                script_path = os.readlink(meta_path)
                if script_path in meta:
                    meta[script_path].append(file)
                else:
                    meta[script_path] = [file]

        return meta

    def get_changes(self, install_root='/'):
        '''Scan the build directories for files that are different than what's in the install root, using sha1 hashes to compare file contents'''
        changed = []
        self.merge_partials()

        def file_hash(path):
            h = sha()
            f = open(path, 'rb')
            chunk = f.read(524288)
            while chunk:
                h.update(chunk)
                chunk = f.read(524288)
            f.close()
            return h.hexdigest()

        if sys.version_info >= (2,6):
            files_to_walk = os.walk(self.build_path, followlinks=True)
        else:
            files_to_walk = os.walk(self.build_path)

        for root, dirs, files in files_to_walk:
            if '.bishop' in dirs:
                dirs.remove('.bishop')
            
            rel_root = root.replace(self.build_path, '')
            if rel_root.startswith('/'):
                rel_root = rel_root[1:]

            for file in files:
                file_path = os.path.join(root, file)
                install_path = os.path.join(install_root, rel_root, file)
                if not os.path.exists(install_path) or file_hash(file_path) != file_hash(install_path):
                    changed.append(os.path.join(rel_root, file))

            if len(files) == 0 and len(dirs) == 0 and rel_root != '':
                install_path = os.path.join(install_root, rel_root)
                # Create orphan directories and add them to the changed list so that the pre/post install scripts will trigger
                if not os.path.isdir(install_path):
                    changed.append(rel_root)

        return changed

    def extract_package(self, package_name, role_name):
        '''Extract the config files a given uninstalled package into a given role'''
        role_path = os.path.join(util.get_repopath(), role_name)
        package.Package().extract(package_name, os.path.join(role_path, 'files'))
        
        # Only keep the files in /etc (a simple way to isolate configuration from other stuff)
        for bad_path in [os.path.join(role_path, 'files', path) for path in os.listdir(os.path.join(role_path, 'files')) if path != 'etc']:
            shutil.rmtree(bad_path)
        
        # Write the package to the packages list (presume the dependencies will always come along for the ride)
        f = open(os.path.join(role_path, 'packages'), 'w')
        f.write(package_name + '\n')
        f.close()

    def lock(self):
        '''Lock this host for modification - prevent multiple installs or builds from running simultaneously, returning True if a new lock was acquired'''
        if self._locked:
            return False
        self._locked = open(os.path.join(self.path, '.lock'), 'w')
        fcntl.flock(self._locked, fcntl.LOCK_EX)
        return True

    def merge_partials(self):
        '''Scan the build directory for any defined partials and merge them into files'''
        meta_path = os.path.join(self.build_path, '.bishop')
        if sys.version_info >= (2,6):
            files_to_walk = os.walk(meta_path, followlinks=True)
        else:
            files_to_walk = os.walk(meta_path)

        for root, dirs, files in files_to_walk:
            rel_root = root.replace(meta_path, '')
            if rel_root.startswith('/'):
                rel_root = rel_root[1:]

            partials = {}
            for file in [f for f in files if '-bpartial-' in f]:
                file_path = os.path.join(root, file)
                name = os.path.join(rel_root, file.split('-bpartial-')[0])
                if name in partials:
                    partials[name].append(file_path)
                else:
                    partials[name] = [file_path]
            
            if len(partials) > 0:
                for name, paths in partials.items():
                    paths.sort()
                    partial_content = '\n'.join([open(path).read() for path in paths])
                    build_path = os.path.join(self.build_path, name)
                    if not os.path.exists(build_path):
                        try:
                            os.makedirs(os.path.dirname(build_path))
                        except OSError:
                            pass
                        open(build_path, 'w').write(partial_content)
                    else:
                        content = open(build_path).read()
                        os.remove(build_path)
                        open(build_path, 'w').write(content + '\n' + partial_content)

    def unlock(self):
        '''Unlock a given lock'''
        if not self._locked:
            return False

        fcntl.flock(self._locked, fcntl.LOCK_UN)
        self._locked.close()
        self._locked = False
        return True

class Remote(object):
    def __init__(self, host):
        if ':' not in host:
            host += ':4200'
        self._server = xmlrpclib.ServerProxy('http://%s' % host, allow_none=True)

    def __getattr__(self, attr):
        try:
            if hasattr(getattr(Local, attr), '__func__'):
                return getattr(self._server, attr)
            else:
                return getattr(self._server, attr)()
        except AttributeError:
            return getattr(self._server, attr)()


class Role(object):
    def __init__(self, repo, role):
        self._hosts = {}
        for host, info in repo.cluster[role].items():
            self._hosts[host] = Remote(info['ip'])

    def __getattr__(self, attr):
        def _getter(*args):
            ret = {}
            for host, server in self._hosts.items():
                ret[host] = getattr(server, attr)(*args)
            return ret
        
        try:
            if hasattr(getattr(Local, attr), '__func__'):
                return _getter
            else:
                return _getter()
        except AttributeError:
            return _getter()
        

