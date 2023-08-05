import os.path
from bishop.mako.template import Template
from bishop.mako.lookup import TemplateLookup
import error, util, platform

class Role(object):
    def __init__(self, host, name):
        self.host = host
        self.name = name
        self._built = False

        if not os.path.exists(self.path):
            raise error.BuildError('No role found with name %s' % name)

    @property
    def path(self):
        '''Return the on-disk path for this role'''
        return os.path.join(self.host.path, self.name)

    @property
    def mixins(self):
        '''Return the list of mixin names that are dependencies of this role'''
        try:
            f = open(os.path.join(self.path, 'mixins'), 'r')
            return util.uncomment_lines(f.read())
            f.close()
        except IOError:
            return []
    
    @property
    def packages(self):
        '''Return a list of package names that must be installed for this role to be installed'''
        try:
            f = open(os.path.join(self.path, 'packages'), 'r')
            return util.uncomment_lines(f.read())
            f.close()
        except IOError:
            return []
    
    def _relative_pathlist(self, dirname):
        '''Extract out the algorithm to return a list of files relative to a subdirectory of a role'''
        rel = []
        file_root = os.path.join(self.path, dirname)
        if not os.path.isdir(file_root):
            return rel

        for root, dirs, walk_files in os.walk(file_root):
            rel_root = root.replace(file_root, '')
            if rel_root.startswith('/'):
                rel_root = rel_root[1:]
            for file in walk_files:
                rel.append(os.path.join(rel_root, file))

            if len(walk_files) == 0 and len(dirs) == 0:
                '''Orphan directories will be added to the install just like files'''
                rel.append(rel_root)

        return rel

    @property
    def files(self):
        '''Return the relative (to the node-root) paths of all files for this role'''
        return self._relative_pathlist('files')

    @property
    def templates(self):
        '''Return the relative (to the node-root) paths of all templates for this role'''
        return self._relative_pathlist('templates')

    @property
    def partials(self):
        '''Return the relative (to the node-root) paths of all partials for this role'''
        return self._relative_pathlist('partials')

    @property
    def pre_install(self):
        preinst_path = os.path.join(self.path, 'preinst')
        if os.path.exists(preinst_path):
            return preinst_path
        return None
    
    @property
    def post_install(self):
        postinst_path = os.path.join(self.path, 'postinst')
        if os.path.exists(postinst_path):
            return postinst_path
        return None

    @property
    def pre_package(self):
        prepackage_path = os.path.join(self.path, 'prepackage')
        if os.path.exists(prepackage_path):
            return prepackage_path
        return None

    def build(self):
        '''Iterate through the role definition and signal to the host how to build the role data on the system'''
        if self._built:
            return

        for path in self.files:
            self.ready(path, link=os.path.join(self.path, 'files', path))

        lookup = TemplateLookup(directories=[os.path.join(self.path, 'templates'), os.path.join(self.path, 'template-includes')], strict_undefined=True)
        partial_lookup = TemplateLookup(directories=[os.path.join(self.path, 'partials'), os.path.join(self.path, 'template-includes')], strict_undefined=True)
        tpl_vars = util.get_tplvars()
        if 'cpu_count' not in tpl_vars: tpl_vars['cpu_count'] = util.cpu_count()
        if 'total_memory' not in tpl_vars: tpl_vars['total_memory'] = util.system_memory()
        if 'primary_ip' not in tpl_vars: tpl_vars['primary_ip'] = self.host.ip
        if 'hostname' not in tpl_vars: tpl_vars['hostname'] = platform.node()

        for path in self.templates:
            try:
                tpl = lookup.get_template(path)
                content = tpl.render(**tpl_vars)
            except Exception, e:
                raise error.TemplateError('%s in template %s/templates/%s' % (str(e), self.name, path))
            self.ready(path, content=content)

        for path in self.partials:
            try:
                tpl = partial_lookup.get_template(path)
                content = tpl.render(**tpl_vars)
                self.ready_partial(path, content)
            except Exception, e:
                raise error.TemplateError('%s in template %s/partials/%s' % (str(e), self.name, path))

        
        for package in self.packages:
            self.host.ready_package(package)
            if self.pre_package:
                self.host.ready_prepackage(self.pre_package, package)

        self._built = True

        for mixin in self.mixins:
            self.host.role(mixin).build()

    def ready(self, path, link=None, content=None):
        '''Fill the given path in the build directory with the given content or symlink'''
        build_path = os.path.join(self.host.build_path, path)
        
        if build_path in self.host._owned:
            conflict_role = self.host._owned[build_path]
            #Conflict resolution - if two roles are trying to get at the same file, the explicit role will win over the mixed-in role.  If both roles are mixed in or both are explicit, the conflict must be resolved by making one of them explicit and the other a mixin
            if conflict_role.name in self.host.roles and not self.name in self.host.roles:
                return
            elif self.name in self.host.roles and conflict_role.name not in self.host.roles:
                self.host._owned[build_path] = None
                os.remove(build_path)
            else:
                raise error.ConflictError('Both %s and %s are trying to install to "%s" - resolve by manually installing only one of the roles using "bishop install ROLENAME"' % (self.name, conflict_role.name, build_path))

        if self.pre_install:
            self.ready_meta(path, self.pre_install, 'preinstall')

        if self.post_install:
            self.ready_meta(path, self.post_install, 'postinstall')

        try:
            os.makedirs(os.path.dirname(build_path))
        except OSError:
            pass

        if link is not None:
            link_path = os.path.abspath(link)
            if not os.path.isdir(link_path) or not os.path.isdir(build_path):
                os.symlink(os.path.abspath(link), build_path)
        elif content is not None:
            f = open(build_path, 'w')
            f.write(content)
            f.close()
        else:
            raise error.BuildError('Trying to ready content at %s without a symlink or template' % path)

        self.host.ready(build_path, self)

    def ready_meta(self, path, meta_path, name):
        '''Attach a metadata file to a given path, tagged with a given name'''
        meta_root = os.path.join(self.host.build_path, '.bishop', os.path.dirname(path))
        try:
            os.makedirs(meta_root)
        except OSError:
            pass
        
        meta_build_path = os.path.join(meta_root, '%s-%s' % (os.path.basename(path), name))
        if os.path.exists(meta_build_path):
            os.remove(meta_build_path)

        os.symlink(os.path.abspath(meta_path), meta_build_path)

    def ready_partial(self, path, content):
        '''Take the rendered partial content and attach it to the file as metadata'''
        meta_root = os.path.join(self.host.build_path, '.bishop', os.path.dirname(path))
        try:
            os.makedirs(meta_root)
        except OSError:
            pass

        meta_build_path = os.path.join(meta_root, '%s-bpartial-%s' % (os.path.basename(path), self.name))
        f = open(meta_build_path, 'w')
        f.write(content)
        f.close()
