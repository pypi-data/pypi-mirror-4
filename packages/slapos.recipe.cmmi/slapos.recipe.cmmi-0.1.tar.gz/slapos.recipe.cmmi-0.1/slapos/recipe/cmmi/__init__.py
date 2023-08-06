import errno
from hashlib import md5
import hexagonit.recipe.download
import imp
import logging
import os
import pkg_resources
from platform import machine as platform_machine
import re
import shutil
import subprocess
import sys
import zc.buildout
from zc.buildout.download import Download


class Recipe(object):
    """zc.buildout recipe for compiling and installing software"""

    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name

        # Merge options if there is a matched platform section
        platform_options = self.get_platform_options()
        if platform_options is None:
            self.original_options = options
        else:
            self.original_options = options.copy()
            options.update(platform_options)

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name)
        prefix = options.get('prefix', '').strip()
        if prefix == '':
            prefix = self.buildout_prefix = buildout['buildout'].get('prefix', '').strip()
            if 'cygwin' != sys.platform:
                self.buildout_prefix = ''
        else:
            self.buildout_prefix = ''
        options['prefix'] = options['location'] if prefix == '' else prefix
        options['url'] = options.get('url', '').strip()
        options['path'] = options.get('path', '').strip()
        options['promises'] = options.get('promises', '')

        # Check dependencies, all the dependent parts will be installed first. It
        # seems once part is referenced, for example, self.buildout[part], it will
        # be appended as an install part.
        # dpendent_parts = options.get('dependencies', '').split()
        # assert isinstance(buildout, zc.buildout.buildout.Buildout)
        # buildout._compute_part_signatures(
        #     [part for part in dpendent_parts if part not in buildout._parts])

        # Calculate md5sum of all the options for each dependent part, and save it
        # as option "dependencies". So if any dependent part changes, zc.buildout
        # will reinstall the part because this option is changed.
        dependencies = []
        for part in options.get('dependencies', '').split():
            m = md5()
            for (k, v) in self.buildout[part].iteritems():
                m.update(v)
            dependencies.append(m.hexdigest())
        options['dependencies'] = ' '.join(dependencies)

        if options['url'] and options['path']:
            raise zc.buildout.UserError('You must use either "url" or "path", not both!')
        if not (options['url'] or options['path']):
            raise zc.buildout.UserError('You must provide either "url" or "path".')

        if options['url']:
            options['compile-directory'] = '%s__compile__' % options['location']
        else:
            options['compile-directory'] = options['path']

        self.environ = {}
        self.original_environment = os.environ.copy()

        environment_section = self.options.get('environment-section', '').strip()
        if environment_section and environment_section in buildout:
            # Use environment variables from the designated config section.
            self.environ.update(buildout[environment_section])
        for variable in self.options.get('environment', '').splitlines():
            if variable.strip():
                try:
                    key, value = variable.split('=', 1)
                    self.environ[key.strip()] = value
                except ValueError:
                    raise zc.buildout.UserError('Invalid environment variable definition: %s', variable)
        # Add prefix to PATH, CPPFLAGS, CFLAGS, CXXFLAGS, LDFLAGS
        if self.buildout_prefix != '':
            self.environ['PATH'] = '%s/bin:%s' % (self.buildout_prefix, self.environ.get('PATH', '/usr/bin'))
            self.environ['CPPFLAGS'] = '-I%s/include %s' % (self.buildout_prefix, self.environ.get('CPPFLAGS', ''))
            self.environ['CFLAGS'] = '-I%s/include %s' % (self.buildout_prefix, self.environ.get('CFLAGS', ''))
            self.environ['CXXFLAGS'] = '-I%s/include %s' % (self.buildout_prefix, self.environ.get('CXXFLAGS', ''))
            self.environ['LDFLAGS'] = '-L%s/lib %s' % (self.buildout_prefix, self.environ.get('LDFLAGS', ''))

        # Extrapolate the environment variables using values from the current
        # environment.
        for key in self.environ:
            self.environ[key] = self.environ[key] % os.environ
        self.environ['TMP'] = os.path.join(options['location'], 'tmp')

    def augmented_environment(self):
        """Returns a dictionary containing the current environment variables
        augmented with the part specific overrides.

        The dictionary is an independent copy of ``os.environ`` and
        modifications will not be reflected in back in ``os.environ``.
        """
        env = os.environ.copy()
        env.update(self.environ)
        return env

    def update(self):
        pass

    def _compute_part_signatures(self, options):
        # Copy from zc.buildout.Buildout, compute recipe signature
        recipe, entry = zc.buildout.buildout._recipe(options)
        req = pkg_resources.Requirement.parse(recipe)
        sig = zc.buildout.buildout._dists_sig(pkg_resources.working_set.resolve([req]))
        return ' '.join(sig)

    def get_platform(self):
        # Get value of sys.platform
        for platform in ['linux', 'cygwin', 'beos', 'darwin', 'atheos', 'osf1',
            'netbsd', 'openbsd',  'freebsd', 'unixware', 'sunos']:
            if sys.platform.startswith(platform):
                return platform
        return sys.platform

    def get_machine(self):
        arch = platform_machine()
        # i?86-*-* : x86
        if arch in ('i386', 'i586', 'i686'):
            return 'x86'
        # x86_64-*-* : amd64
        elif arch == 'x86_64':
            return 'amd64'
        # ia64-*-* : ia64
        # and others
        return arch

    def get_platform_options(self):
        platform_part = self.get_platform() + '-' + self.name
        part_list = [part for part in self.buildout if part.endswith(platform_part)]
        if part_list[:1]:
            arch_prefix = self.get_machine() + '-'
            for part in part_list:
                if part.startswith(arch_prefix):
                    return self.buildout[part]
            else:
                return self.buildout.get(platform_part)

    def download_file(self, url):
        download = Download(self.buildout['buildout'])
        url, _s_, md5sum = url.partition('#')
        return download(url, md5sum=None if md5sum == '' else md5sum)

    def get_installed_files(self, ref_file):
        # if [buildout] has option 'prefix', then return all the files
        # in this path which create time is newer than ref_file.
        # Exclude directory and don't follow link.
        assert self.buildout_prefix
        log = logging.getLogger(self.name)
        cmd = 'find %s -cnewer %s ! -type d' % (self.buildout_prefix, ref_file)
        try:
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            files, _i_ = p.communicate()
            retcode = p.returncode
            if retcode < 0:
                log.error('Command received signal %s: %s' % (-retcode, cmd))
                raise zc.buildout.UserError('System error')
            elif retcode > 0:
                log.error('Command failed with exit code %s: %s' % (retcode, cmd))
                raise zc.buildout.UserError('System error')
        except OSError, e:
            log.error('Command failed: %s: %s' % (e, cmd))
            raise zc.buildout.UserError('System error')
        return files.split()
        
    def check_promises(self):
        result = True
        log = logging.getLogger(self.name)        
        for path in self.options['promises'].splitlines():
            if not os.path.exists(path):
                result = False
                log.warning('could not find promise "%s"' % path)
        return result
        
    def call_script(self, script):
        """This method is copied from z3c.recipe.runscript.

        See http://pypi.python.org/pypi/z3c.recipe.runscript for details.
        """
        url, callable = script.rsplit(':', 1)
        filename, is_temp = self.download_file(url)
        if not is_temp:
            filename = os.path.abspath(filename)
        module = imp.load_source('script', filename)
        script = getattr(module, callable.strip())

        try:
            script(self.options, self.buildout, self.augmented_environment())
        except TypeError:
            # BBB: Support hook scripts that do not take the environment as
            # the third parameter
            script(self.options, self.buildout)
        finally:
            if is_temp:
                os.remove(filename)

    def run(self, cmd):
        """Run the given ``cmd`` in a child process."""
        log = logging.getLogger(self.name)
        try:
            retcode = subprocess.call(cmd, shell=True, env=self.augmented_environment())

            if retcode < 0:
                log.error('Command received signal %s: %s' % (-retcode, cmd))
                raise zc.buildout.UserError('System error')
            elif retcode > 0:
                log.error('Command failed with exit code %s: %s' % (retcode, cmd))
                raise zc.buildout.UserError('System error')
        except OSError as e:
            log.error('Command failed: %s: %s' % (e, cmd))
            raise zc.buildout.UserError('System error')

    def install(self):
        log = logging.getLogger(self.name)
        parts = []

        make_cmd = self.options.get('make-binary', 'make').strip()
        make_options = ' '.join(self.options.get('make-options', '').split())
        make_targets = ' '.join(self.options.get('make-targets', 'install').split())

        configure_options = self.options.get('configure-options', '').split()
        configure_cmd = self.options.get('configure-command', '').strip()

        if not configure_cmd:
            # Default to using basic configure script.
            configure_cmd = './configure'
            # Inject the --prefix parameter if not already present
            if '--prefix' not in ' '.join(configure_options):
                configure_options.insert(0, '--prefix=\"%s\"' % self.options['prefix'])
        elif make_cmd == 'make' and make_targets == 'install':
            make_targets += ' prefix=\"%s\"' % self.options['prefix']

        patch_cmd = self.options.get('patch-binary', 'patch').strip()
        patch_options = ' '.join(self.options.get('patch-options', '-p0').split())
        patches = self.options.get('patches', '').split()

        if self.environ:
            for key in sorted(self.environ.keys()):
                log.info('[ENV] %s = %s', key, self.environ[key])

        # Download the source using hexagonit.recipe.download
        if self.options['url']:
            compile_dir = self.options['compile-directory']
            if os.path.exists(compile_dir):
                # leftovers from a previous failed attempt, removing it.
                log.warning('Removing already existing directory %s' % compile_dir)
                shutil.rmtree(compile_dir)
            os.mkdir(compile_dir)
            try:
                opt = self.options.copy()
                opt['destination'] = compile_dir
                hexagonit.recipe.download.Recipe(
                    self.buildout, self.name, opt).install()
            except:
                shutil.rmtree(compile_dir)
                raise
        else:
            log.info('Using local source directory: %s' % self.options['path'])
            compile_dir = self.options['path']

        current_dir = os.getcwd()
        try:
            os.mkdir(self.options['location'])
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
        os.chdir(compile_dir)
        tmp_path = self.environ['TMP']
        shutil.rmtree(tmp_path, True)
        os.mkdir(tmp_path)

        try:
            try:
                # We support packages that either extract contents to the $PWD
                # or alternatively have a single directory.
                contents = os.listdir(compile_dir)
                if len(contents) == 1 and os.path.isdir(contents[0]):
                    # Single container
                    os.chdir(contents[0])

                if patches:
                    log.info('Applying patches')
                    for patch in patches:
                        patch_filename, is_temp = self.download_file(patch)
                        self.run('%s %s < %s' % (patch_cmd, patch_options, patch_filename))
                        if is_temp:
                            os.remove(path_filename)

                if 'pre-configure-hook' in self.options and len(self.options['pre-configure-hook'].strip()) > 0:
                    log.info('Executing pre-configure-hook')
                    self.call_script(self.options['pre-configure-hook'])

                pre_configure_cmd = self.options.get('pre-configure', '').strip() % self.options
                if pre_configure_cmd != '':
                    log.info('Executing pre-configure')
                    self.run(pre_configure_cmd)

                self.run(('%s %s' % (configure_cmd, ' '.join(configure_options))) % self.options)

                if 'pre-make-hook' in self.options and len(self.options['pre-make-hook'].strip()) > 0:
                    log.info('Executing pre-make-hook')
                    self.call_script(self.options['pre-make-hook'])

                pre_build_cmd = self.options.get('pre-build', '').strip() % self.options
                if pre_build_cmd != '':
                    log.info('Executing pre-build')
                    self.run(pre_build_cmd)

                self.run(('%s %s' % (make_cmd, make_options)) % self.options)

                pre_install_cmd = self.options.get('pre-install', '').strip() % self.options
                if pre_install_cmd != '':
                    log.info('Executing pre-install')
                    self.run(pre_install_cmd)

                self.run(('%s %s %s' % (make_cmd, make_options, make_targets)) % self.options)

                if 'post-make-hook' in self.options and len(self.options['post-make-hook'].strip()) > 0:
                    log.info('Executing post-make-hook')
                    self.call_script(self.options['post-make-hook'])

                post_install_cmd = self.options.get('post-install', '').strip() % self.options
                if post_install_cmd != '':
                    log.info('Executing post-install')
                    self.run(post_install_cmd)
                if self.buildout_prefix != '' and os.path.exists(self.buildout_prefix):
                    log.info('Getting installed file lists')
                    parts.extend(self.get_installed_files(tmp_path))
            except:
                log.error('Compilation error. The package is left as is at %s where '
                          'you can inspect what went wrong' % os.getcwd())
                raise
        finally:
            os.chdir(current_dir)
            shutil.rmtree(tmp_path)

        # Check promises
        self.check_promises()
        
        if self.options['url']:
            if self.options.get('keep-compile-dir',
                self.buildout['buildout'].get('keep-compile-dir', '')).lower() in ('true', 'yes', '1', 'on'):
                # If we're keeping the compile directory around, add it to
                # the parts so that it's also removed when this recipe is
                # uninstalled.
                parts.append(self.options['compile-directory'])
            else:
                shutil.rmtree(compile_dir)
                del self.options['compile-directory']

        parts.append(self.options['location'])
        return parts
