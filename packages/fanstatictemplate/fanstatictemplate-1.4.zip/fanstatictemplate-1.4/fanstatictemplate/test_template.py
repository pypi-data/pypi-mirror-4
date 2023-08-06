import pytest

from paste.script.create_distro import CreateDistroCommand

from fanstatictemplate import Template

def test_template(tmpdir):
    tmpdir.chdir()
    t = Template('foo')
    command = CreateDistroCommand('create')
    args = ['-t', 'fanstatic', 'js.foo', 'library_name=foo',
        'library_version=1.1.1', 'library_url=http://www.foo.org']
    command.run(args)
    package_dir = tmpdir.join('js.foo')
    # test the template_metadata
    assert sorted([item.basename for item in package_dir.listdir()]) == \
        ['.hgignore', 'CHANGES.txt', 'LICENSE.txt','MANIFEST.in', 'README.txt',
        'bootstrap.py', 'buildout.cfg', 'js', 'js.foo.egg-info', 'setup.py']
    # test the template_code
    assert sorted([item.basename for item in package_dir.join('js').join('foo').listdir()]) == \
        ['__init__.py', 'resources', 'test_foo.txt']

def test_arbitrarily_deep_packages(tmpdir):
    tmpdir.chdir()
    command = CreateDistroCommand('create')
    args = ['-t', 'fanstatic', 'one.two.three.four', 'library_name=foo',
        'library_version=1.1.1', 'library_url=http://www.foo.org']
    command.run(args)
    resultdir = tmpdir.join('one.two.three.four')
    assert resultdir.join('one').check()
    assert resultdir.join('one').join('two').check()
    assert resultdir.join('one').join('two').join('three').check()
    assert resultdir.join('one').join('two').join('three').join('four').check()

def test_namespace_packages(tmpdir):
    tmpdir.chdir()
    command = CreateDistroCommand('create')
    args = ['-t', 'fanstatic', 'foo', 'library_name=foo',
        'library_version=1.1.1', 'library_url=http://www.foo.org']
    command.run(args)
    setup_py = tmpdir.join('foo').join('setup.py').read()
    assert 'namespace_packages=' not in setup_py
