from zope.testing import renormalizing
import doctest
import errno
import os
import re
import shutil
import stat
import tarfile
import tempfile
from time import sleep
import zc.buildout
import zc.buildout.testing
import zc.buildout.tests

try:
    import unittest2 as unittest
except ImportError:
    import unittest

optionflags = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install('hexagonit.recipe.download', test)
    zc.buildout.testing.install_develop('slapos.recipe.cmmi', test)

class NonInformativeTests(unittest.TestCase):

    def setUp(self):
        self.dir = os.path.realpath(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir)
        for var in list(os.environ.keys()):
            if var.startswith('HRC_'):
                del os.environ[var]

    def write_file(self, filename, contents, mode=stat.S_IREAD | stat.S_IWUSR):
        path = os.path.join(self.dir, filename)
        fh = open(path, 'w')
        fh.write(contents)
        fh.close()
        os.chmod(path, mode)
        return path

    def make_recipe(self, buildout, name, options, **buildout_options):
        from slapos.recipe.cmmi import Recipe
        parts_directory_path = os.path.join(self.dir, 'test_parts')
        try:
            os.mkdir(parts_directory_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        bo = {
            'buildout': {
                'parts-directory': parts_directory_path,
                'directory': self.dir,
            }
        }
        bo.update(buildout)
        bo['buildout'].update(buildout_options)
        return Recipe(bo, name, options)

    def test_working_directory_restored_after_failure(self):
        compile_directory = os.path.join(self.dir, 'compile_directory')
        os.makedirs(compile_directory)
        recipe = self.make_recipe({}, 'test', {'path': compile_directory})
        os.chdir(self.dir)

        with self.assertRaises(zc.buildout.UserError):
            recipe.install()
        self.assertEqual(self.dir, os.getcwd())

    def test_working_directory_restored_after_success(self):
        compile_directory = os.path.join(self.dir, 'compile_directory')
        os.makedirs(compile_directory)
        self.write_file(os.path.join(compile_directory, 'configure'), 'Dummy configure')

        self.make_recipe({}, 'test', {'path': compile_directory})
        os.chdir(self.dir)
        self.assertEqual(self.dir, os.getcwd())

    def test_compile_directory_exists(self):
        """
        Do not fail if the compile-directory already exists
        """
        compile_directory = os.path.join(self.dir, 'test_parts/test__compile__')
        os.makedirs(compile_directory)

        recipe = self.make_recipe({}, 'test', dict(url="some invalid url"))
        os.chdir(self.dir)

        # if compile directory exists, recipe should raise an IOError because
        # of the bad URL, and _not_ some OSError because test__compile__
        # already exists
        with self.assertRaises(IOError):
            recipe.install()

    def test_restart_after_failure(self):
        temp_directory = tempfile.mkdtemp(dir=self.dir, prefix="fake_package")

        configure_path = os.path.join(temp_directory, 'configure')
        self.write_file(configure_path, 'exit 0', mode=stat.S_IRWXU)
        makefile_path = os.path.join(temp_directory, 'Makefile')
        self.write_file(makefile_path, 'all:\n\texit -1')

        os.chdir(temp_directory)

        ignore, tarfile_path = tempfile.mkstemp(suffix=".tar")
        tar = tarfile.open(tarfile_path, 'w')
        tar.add('configure')
        tar.add('Makefile')
        tar.close()

        recipe = self.make_recipe({}, 'test', {'url': tarfile_path})
        os.chdir(self.dir)

        try:
            # expected failure
            with self.assertRaises(zc.buildout.UserError):
                recipe.install()

            # the install should still fail, and _not_ raise an OSError
            with self.assertRaises(zc.buildout.UserError):
                recipe.install()
        finally:
            try:
                shutil.rmtree(temp_directory)
                os.remove(tarfile_path)
            except:
                pass

    def test_environment_restored_after_building_a_part(self):
        # Make sure the test variables do not exist beforehand
        self.failIf('HRC_FOO' in os.environ)
        self.failIf('HRC_BAR' in os.environ)
        # Place a sentinel value to make sure the original environment is
        # maintained
        os.environ['HRC_SENTINEL'] = 'sentinel'
        self.assertEqual(os.environ.get('HRC_SENTINEL'), 'sentinel')

        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            'environment': 'HRC_FOO=bar\nHRC_BAR=foo'})
        os.chdir(self.dir)
        recipe.install()

        # Make sure the test variables are not kept in the environment after
        # the part has been built.
        self.failIf('HRC_FOO' in os.environ)
        self.failIf('HRC_BAR' in os.environ)
        # Make sure the sentinel value is still in the environment
        self.assertEqual(os.environ.get('HRC_SENTINEL'), 'sentinel')

    def test_run__unknown_command(self):
        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__)})
        with self.assertRaises(zc.buildout.UserError):
            recipe.run('this-command-does-not-exist')

    def test_call_script__bbb_for_callable_with_two_parameters(self):
        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
        })

        # The hook script does not return anything so we (ab)use exceptions
        # as a mechanism for asserting the function behaviour.
        filename = os.path.join(self.dir, 'hooks.py')
        script = open(filename, 'w')
        script.write('def my_hook(options, buildout): raise ValueError("I got called")\n')
        script.close()

        try:
            recipe.call_script('%s:my_hook' % filename)
            self.fail("The hook script was not called.")
        except ValueError as e:
            self.assertEqual(str(e), 'I got called')

    def test_call_script__augmented_environment_as_third_parameter(self):
        os.environ['HRC_SENTINEL'] = 'sentinel'
        os.environ['HRC_TESTVAR'] = 'foo'

        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            'environment': 'HRC_TESTVAR=bar'
        })

        # The hook script does not return anything so we (ab)use exceptions
        # as a mechanism for asserting the function behaviour.
        filename = os.path.join(self.dir, 'hooks.py')
        script = open(filename, 'w')
        script.write('def my_hook(options, buildout, env): raise ValueError("%(HRC_SENTINEL)s %(HRC_TESTVAR)s" % env)\n')
        script.close()

        try:
            recipe.call_script('%s:my_hook' % filename)
            self.fail("The hook script was not called.")
        except ValueError as e:
            self.assertEqual(str(e), 'sentinel bar')

    def no_test_make_target_with_prefix(self):
        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            'configure-command' : './configure',
            'pre-install' : 'sed -i -e "s/installing package/installing package at \$\$prefix /g" Makefile',
            })
        os.chdir(self.dir)
        recipe.install()

        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            'pre-install' : 'sed -i -e "s/installing package/installing package at \$\$prefix /g" Makefile',
            'make-targets' : 'install-lib prefix=%(prefix)s',
            })
        recipe.install()

    def test_download_file(self):
        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            })
        url = '%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__)
        file, is_temp = recipe.download_file(url)
        self.assertFalse(is_temp)
        self.assertEquals(file, url)

        url = 'ftp://ftp.gnu.org/welcome.msg'
        file, is_temp = recipe.download_file(url)
        self.assertTrue(is_temp)
        self.assertTrue(os.path.exists(file))

        url = 'ftp://ftp.gnu.org/welcome.msg#ec7ab8024467ba3b6e173c57fd4990f6'
        file, is_temp = recipe.download_file(url)
        self.assertTrue(is_temp)
        self.assertTrue(os.path.exists(file))

        url = 'ftp://ftp.gnu.org/welcome.msg#0205'
        self.assertRaises(zc.buildout.download.ChecksumError, recipe.download_file, url)

    def test_buildout_prefix(self):
        buildout_prefix = os.path.join(self.dir, 'test_parts/test_local')
        os.makedirs(buildout_prefix)

        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            },
            prefix=buildout_prefix
            )
        self.assertEquals(recipe.options.get('prefix'), buildout_prefix)

        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            'prefix' : self.dir,
            },
            prefix=buildout_prefix
            )
        self.assertEquals(recipe.options.get('prefix'), self.dir)

    def test_get_installed_files(self):
        prefix = os.path.join(self.dir, 'test_parts/test_local')
        os.makedirs(prefix)

        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            })
        os.chdir(self.dir)

        # The hook script does not return anything so we (ab)use exceptions
        # as a mechanism for asserting the function behaviour.
        no_installed_files = ('a.txt', 'b.txt', 'c', 'c/d.txt')
        installed_files = ['e.txt', 'f.txt', 'g', 'g/h.txt']
        for s in no_installed_files:
            if s.endswith('.txt'):
                f = open(os.path.join(prefix, s), 'w')
                f.write(s)
                f.close()
            else:
                os.makedirs(os.path.join(prefix, s))
        sleep(2)
        ref_path = os.path.join(self.dir, 'refs')
        os.makedirs(ref_path)
        sleep(2)
        for s in installed_files:
            if s.endswith('.txt'):
                f = open(os.path.join(prefix, s), 'w')
                f.write(s)
                f.close()
            else:
                os.makedirs(os.path.join(prefix, s))
        recipe.buildout_prefix = prefix
        file_list = recipe.get_installed_files(ref_path)
        installed_files.pop(2)
        self.assertEquals([os.path.relpath(f, prefix) for f in file_list], installed_files)

    def test_honor_buidlout_keep_compile_directory(self):
        buildout = {'keep-compile-dir' : 'true'}
        recipe = self.make_recipe({}, 'test', {
            'url': 'file://%s/testdata/package-0.0.0.tar.gz' % os.path.dirname(__file__),
            },
            **buildout
            )
        os.chdir(self.dir)
        recipe.install()

        build_directory = os.path.join(self.dir, 'test_parts/test__compile__')
        self.assertTrue(os.path.exists(build_directory))

def test_suite():
    suite = unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=optionflags,
            checker=renormalizing.RENormalizing([
                (re.compile('--prefix=\S+sample-buildout'),
                 '--prefix=/sample_buildout'),
                (re.compile('\s/\S+sample-buildout'),
                 ' /sample_buildout'),
                zc.buildout.testing.normalize_path,
            ]),
        ),
        unittest.makeSuite(NonInformativeTests),
    ))
    return suite
