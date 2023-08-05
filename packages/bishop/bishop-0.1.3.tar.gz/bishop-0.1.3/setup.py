from distutils.core import setup, Command
import os.path, shutil

class role_cmd(Command):
    description = 'install bishop into a directory as a bishop role'
    user_options = [
        ('role-dir=', 'd', 'directory to install the role into')
    ]

    def initialize_options(self):
        self.role_dir = './build.bishop.role'

    def finalize_options(self):
        parent_dir = os.path.dirname(self.role_dir)
        if parent_dir == '':
            parent_dir = '.'

        if not os.path.isdir(parent_dir):
            raise ValueError('Cannot save bishop role - "%s" is not a directory or does not exist' % parent_dir)

    def run(self):
        if not os.path.isdir(self.role_dir):
            os.makedirs(self.role_dir)
        
        src_root = os.path.join(self.role_dir, 'files/usr/local/src/bishop')
        if not os.path.isdir(src_root):
            os.makedirs(src_root)

        for path in ['bishop', 'scripts', 'data', 'setup.py']:
            dest = os.path.join(src_root, path)
            if os.path.isdir(dest):
                shutil.rmtree(dest)

            if os.path.isdir(path):
                shutil.copytree(path, os.path.join(src_root, path), ignore=lambda path, files: [file for file in files if file.endswith('.pyc')])
            else:
                shutil.copy(path, os.path.join(src_root, path))
        
        postinst = open(os.path.join(self.role_dir, 'postinst'), 'w')
        postinst.write('#!/bin/sh\n\ncd /usr/local/src/bishop\nchmod +x /usr/local/src/bishop/data/bishop-install\npython setup.py install\n')
        postinst.close()
        os.chmod(os.path.join(self.role_dir, 'postinst'), 0755)
        print 'Bishop copied as role to %s' % self.role_dir


setup(name='bishop', version='0.1.3', description='Simple Configuration Management',
      author='Chad Morris', author_email='chadwickmorris@gmail.com',
      license='MIT', keywords='configuration management',
      url='http://projects.chadwickmorris.com/bishop/', packages=['bishop', 'bishop.mako', 'bishop.mako.ext'],
      scripts=['scripts/bishop'], cmdclass={'install_role': role_cmd},
      data_files=[('/etc/cron.hourly', ['data/bishop-install'])],
      requires=['pexpect'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Topic :: System :: Installation/Setup'
      ]
)
