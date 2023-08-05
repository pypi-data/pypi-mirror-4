import bishop
import os, os.path, shutil
from nose import tools

host = None

def setup_test():
    global host
    
    if os.path.isdir('test/test-install'):
        shutil.rmtree('test/test-install')
    
    for path in [os.path.join('test/test-repo', p) for p in os.listdir('test/test-repo') if p.startswith('.')]:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    
    # Mercurial removes empty directories, but we explicitly need an empty directory for some of the tests
    if not os.path.isdir('test/test-repo/roledir/files/etc/empty-dir'):
        os.makedirs('test/test-repo/roledir/files/etc/empty-dir', 0755)
    if not os.path.isdir('test/test-repo/rolepostinst/files/etc/empty-dir'):
        os.makedirs('test/test-repo/rolepostinst/files/etc/empty-dir', 0755)
    
    open('/tmp/setup-calls.log', 'a').write('setting up...\n')
    host = bishop.host.Local(path='test/test-repo')

def teardown_test():
    global host
    host.unlock()
    host = None
    if os.path.isdir('test/test-install'):
        shutil.rmtree('test/test-install')
    
    for path in [os.path.join('test/test-repo', p) for p in os.listdir('test/test-repo') if p.startswith('.')]:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    
    bishop.util.vars_path = '/etc/bishop-vars.json'
    bishop.util._tplvars = None


@tools.with_setup(setup_test, teardown_test)
def test_mirror():
    '''Every node will hold their own repository, but will only mirror the roles necessary to install on the node'''
    master_repo = bishop.repo.Repository(path=os.path.abspath('test/test-repo'))
    host = bishop.host.Local(path='test/test-repo/.copy')
    host.repo = master_repo

    host.mirror(['role1'])
    assert os.path.isdir('test/test-repo/.copy/role1')
    assert os.path.exists('test/test-repo/.copy/role1/mixins')
    assert os.path.isdir('test/test-repo/.copy/role1child')
    assert not os.path.isdir('test/test-repo/.copy/role2')
    assert not os.path.isdir('test/test-repo/.copy/.build')

@tools.with_setup(setup_test, teardown_test)
def test_build():
    '''Building a repository should create a .build directory in the repository root holding symlinks to all the files to install'''
    host.build(['role1', 'role2'])
    assert os.path.isdir('test/test-repo/.build')
    assert os.path.exists('test/test-repo/.build/rootfile')
    assert os.path.exists('test/test-repo/.build/etc/sample.conf')
    assert os.path.exists('test/test-repo/.build/etc/other_sample.conf')

@tools.with_setup(setup_test, teardown_test)
def test_build_templates():
    host.build(['role3'])
    assert os.path.exists('test/test-repo/.build/etc/templated.conf')
    assert open('test/test-repo/.build/etc/templated.conf').read().strip() == 'Hello World!'

@tools.with_setup(setup_test, teardown_test)
def test_build_packages():
    host.build(['role5'])
    assert open('test/test-repo/.build/.bishop/packages').read().strip() == 'lynx'

@tools.with_setup(setup_test, teardown_test)
def test_build_prepostinst():
    host.build(['role6'])
    assert os.path.exists('test/test-repo/.build/.bishop/etc/config.conf-postinstall')
    assert not os.path.exists('test/test-repo/.build/.bishop/etc/config.conf-preinstall')

@tools.with_setup(setup_test, teardown_test)
def test_build_node():
    host.roles = ['role2']
    host.build()
    assert os.path.exists('test/test-repo/.build/etc/sample.conf')
