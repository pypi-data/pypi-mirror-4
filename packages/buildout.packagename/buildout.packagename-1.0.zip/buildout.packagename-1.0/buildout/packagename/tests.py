from os import chdir
from os.path import join
from string import strip
from textwrap import dedent
from subprocess import check_call, check_output
from pkg_resources import get_distribution


name = 'buildout.packagename'
home = get_distribution(name).location


def extract_buildout():
    indented = lambda line: line.startswith('  ')
    lines = filter(indented, open(join(home, 'README.rst')))
    return '\n'.join(map(strip, lines))


def test_buildout_uses_package_name(tmpdir):
    buildout = tmpdir.join('buildout.cfg')
    buildout.write(extract_buildout())
    tmpdir.join('setup.py').write(dedent("""
        from setuptools import setup
        setup(name='foo', version='1.0', packages=['foo'])
    """))
    tmpdir.mkdir('foo').join('__init__.py').write(dedent("""
        print 'hello!'
    """))
    chdir(str(tmpdir))
    check_call([join(home, 'bin', 'buildout')])
    app = tmpdir.join('bin', 'app')
    app.check(file=True)
    assert check_output([str(app), '-c', 'import foo']) == 'hello!\n'
