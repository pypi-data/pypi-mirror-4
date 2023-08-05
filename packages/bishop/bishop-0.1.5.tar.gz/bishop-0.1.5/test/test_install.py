import bishop, os, shutil
from nose import tools

host = None

def setup_test():
    global host
    host = bishop.host.Local(path='test/test-repo')
    if os.path.isdir('test/test-install'):
        shutil.rmtree('test/test-install')

    # Mercurial removes empty directories, but we explicitly need an empty directory for some of the tests
    if not os.path.isdir('test/test-repo/roledir/files/etc/empty-dir'):
        os.makedirs('test/test-repo/roledir/files/etc/empty-dir', 0755)
    if not os.path.isdir('test/test-repo/rolepostinst/files/etc/empty-dir'):
        os.makedirs('test/test-repo/rolepostinst/files/etc/empty-dir', 0755)

def teardown_test():
    global host
    host.unlock()
    host = None
    if os.path.isdir('test/test-install'):
        shutil.rmtree('test/test-install')
    
    bishop.util.vars_path = '/etc/bishop-vars.json'
    bishop.util._tplvars = None


@tools.raises(bishop.error.PackageError)
@tools.with_setup(setup_test, teardown_test)
def test_badinstall():
    host.roles = ['role4']
    host.install(path='test/test-install')

@tools.with_setup(setup_test, teardown_test)
def test_goodinstall():
    host.roles = ['role1', 'role5']
    host.install(path='test/test-install')
    assert os.path.exists('test/test-install/etc/other_sample.conf')

@tools.with_setup(setup_test, teardown_test)
def test_installdir():
    '''An empty directory should still be created on install (eliminate need of superfluous .empty files)'''
    host.roles = ['roledir']
    host.install(path='test/test-install')
    assert os.path.exists('test/test-install/etc/empty-dir')

@tools.with_setup(setup_test, teardown_test)
def test_installdir_conflict():
    '''An empty directory that conflicts with a non-empty directory in a separate role should be maintained in the change list but ignored'''
    host.roles = ['roledir', 'roleconflictdir']
    host.install(path='test/test-install')
    assert os.path.exists('test/test-install/etc/empty-dir/not-empty')

@tools.with_setup(setup_test, teardown_test)
def test_orphan_postinstall():
    '''A postinstall script should be run on its own even if it has no files backing it - instead changes to the script itself will trigger rerun'''
    host.roles = ['rolepostinst']
    host.install(path='test/test-install')
    assert os.path.exists('/tmp/tmp-bishoptest-orphan-postinst')

@tools.with_setup(setup_test, teardown_test)
def test_bishopvars():
    '''A JSON object stored in /etc/bishop-vars.json should be implicitly used to create the context object for templates'''
    bishop.util.vars_path = 'test/test-repo/test-vars.json'
    bishop.util._tplvars = None
    
    host.roles = ['roletplvars']
    host.install(path='test/test-install')
    assert os.path.exists('test/test-install/test.txt')
    assert open('test/test-install/test.txt', 'r').read().strip() == 'Message: Hello World!'

@tools.with_setup(setup_test, teardown_test)
def test_partial():
    '''A role that claims a file and a partial for the file should include the content of both the file and the partial'''
    host.roles = ['partialrole']
    host.install(path='test/test-install')
    content = open('test/test-install/test.txt', 'r').read()
    assert content.strip() == 'files content\n\npartials content'

@tools.with_setup(setup_test, teardown_test)
def test_orphan_partial():
    '''A file that has a partial defined but no owning role should still contain the partials content'''
    host.roles = ['orphanpartial']
    host.install(path='test/test-install')
    content = open('test/test-install/test.txt', 'r').read()
    assert content.strip() == 'partials content'
