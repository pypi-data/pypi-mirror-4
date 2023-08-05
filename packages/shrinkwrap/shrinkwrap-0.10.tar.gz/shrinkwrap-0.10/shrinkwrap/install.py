'''utilities for installing shrinkwrapped packages'''
import tarfile
import subprocess
from setuptools.command import install as _install
from distutils import log
import os
import multiprocessing
import platform
import collections
from distutils.errors import DistutilsSetupError

def assert_string(dist, attr, value):
    '''Verify that value is a string'''
    if not isinstance(value, str):
        raise DistutilsSetupError(
            "%r must be a string value (got %r)" % (attr,value)
        )

def assert_callable(dist, attr, value):
    '''Verify that value is a callable function'''
    if callable(value):
        return # OK
    else:
        raise DistutilsSetupError(
            "%r must be a callable function (got %r)" % (attr,value)
        )

def validate_installer_option(dist, attr, value):
    '''Verify that value is either an allowed string or a callable function'''
    if callable(value):
        return # OK
    elif isinstance(value, str) and value in install_functions:
        return # OK
    else:
        raise DistutilsSetupError(
            "%r must be a callable function or valid string option (got %r)" % (attr,value)
        )


class ShrinkwrapInstall(_install.install):
    '''Base class for a setup.py "install" command that wraps a generic tarball installation.'''
    def initialize_options(self):
        _install.install.initialize_options(self)

    def finalize_options(self):
        _install.install.finalize_options(self)

    def download_url(self, url, saveto=None):
        '''Downloads a file.  If no saveto is specified, the basename of
        the URL and the current directory will be used.

          Returns the full path to the saved file on disk.
        '''
        # Implementation borrowed from distribute_setup.py
        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib2 import urlopen

        src = dst = None
        if saveto is None:
            saveto = os.path.basename(url)
        if not os.path.exists(saveto):
            try:
                log.warn("Downloading %s", url)
                src = urlopen(url)
                # Read all at once to avoid writing partial file
                data = src.read()
                dst = open(saveto, 'wb')
                dst.write(data)
            finally:
                if src:
                    src.close()
                if dst:
                    dst.close()
        return os.path.realpath(saveto)

    def untar(self, source, target='.', makedir=False):
        '''Unpack tar file with filename ``source`` to directory ``target``.
        If ``makedir`` is true, then the target directory will be created first,
        including missing parent directories.

        Default is to extract to current directory.
        '''
        tar = tarfile.open(source)
        target = os.path.realpath(target)
        if not os.path.exists(target):
            os.makedirs(target)
        tar.extractall(path=target)
        tar.close()

    def download_and_unpack_tarball(self, url, to_src_dir=False):
        '''Convenience method that downloads a tarball from the given URL and
        unpacks it.  By default, the tarfile and uncompressed contents are placed
        in the current directory, but if to_src_dir is True, then both the tarfile
        and contents will be in the src/ directory under the virtualenv base.

        Returns the full path to the downloaded tar file.
        '''

        initial_working_dir = os.path.realpath(os.getcwd())

        if to_src_dir:
            if not os.path.exists(self.src_dir):
                os.makedirs(self.src_dir)
            os.chdir(self.src_dir)
        tarball = self.download_url(url)
        self.untar(tarball)

        os.chdir(initial_working_dir)

        return tarball

    def shell(self, cmd, success_return_code=0):
        '''Runs ``cmd`` in a shell.  Raises subprocess.CalledProcessError if the
        return code from ``cmd`` is not equal to ``success_return_code``.'''
        log.warn('Executing: ' + cmd)
        ret = subprocess.call('eval $(shrinkwrap activate) && ' + cmd, shell=True, executable='/bin/bash')
        if ret != success_return_code:
            raise subprocess.CalledProcessError(cmd=cmd, returncode=ret)

    def cmd_output(self, cmd, success_return_code=0):
        '''Run command in the shell and return its output as a byte string.

        If return code from command not equal to ``success_return_code``,
        raises subprocess.CalledProcessError.

        Based on implementation from: https://gist.github.com/1027906
        '''
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            error = subprocess.CalledProcessError(retcode, cmd)
            error.output = output
            raise error
        return output
        
    def make(self, parallel=True, extra_opts=None):
        '''Run make in current directory.  If ``parallel`` is true,
        will run make with the -j option and the number of CPU cores.
        ``extra_opts`` is a list of additional options to be passed to make.

        Remember to escape them for the shell, if needed!
        '''
        if parallel:
            cmd = 'make -j%d' % self.ncpu
        else:
            cmd = 'make'

        if extra_opts is not None:
            cmd += ' ' + ' '.join(extra_opts)

        self.shell(cmd)

    def install_env(self, filename, contents):
        '''Create an environment shell script called ``filename`` in the
        shrinkwrap env directory and fill it with the string ``contents``.'''
        fullpath = os.path.join(self.env_dir, filename)
        log.warn('Creating ' + fullpath)
        with open(fullpath, 'w') as f:
            f.write(contents)

    #### Main command interface ####

    def run(self):
        '''setuptools install command that install dependencies in
        before calling the installer function provided in the shrinkwrap_installer
        keyword argument to setup().
        '''
        # Install dependencies
        build_deps = getattr(self.distribution, 'shrinkwrap_requires', None)
        if build_deps is None:
            build_deps = []
        for dep in build_deps:
            build_dir = os.path.join(self.virtualenv, 'build', 'build_' + dep)
            self.shell('pip install -b ' + build_dir + ' ' + dep)

        skip = getattr(self.distribution, 'shrinkwrap_skip', None)

        # Test if we need to actually install anything
        if skip is None or not skip(self):
            # Do the install process for this package
            installer = self.distribution.shrinkwrap_installer
            if installer in install_functions:
                installer = install_functions[installer]

            installer(self)
        else:
            log.warn('Package already installed.  Skipping...')

        # Now finish up and register installation
        _install.install.run(self)


    #### Useful properties ####

    @property
    def virtualenv(self):
        '''Full path to base of virtualenv directory.'''
        return os.path.realpath(os.environ['VIRTUAL_ENV'])

    @property
    def src_dir(self):
        '''Full path to source directory inside virtualenv'''
        return os.path.join(self.virtualenv, 'src')

    @property
    def env_dir(self):
        '''Full path to shrinkwrap env directory inside virtualenv'''
        return os.path.join(self.virtualenv, 'env.d')

    @property
    def ncpu(self):
        '''Number of CPU cores.'''
        return multiprocessing.cpu_count()

    @property
    def python_libdir(self):
        '''Location of python library.'''
        return os.path.join(self.virtualenv, 'lib', 'python%s.%s' % platform.python_version_tuple()[:2], 'config')


def autoconf_install(self):
    '''A convenience function to perform an autoconf-based installation.
    
    Note: requires parameter "shrinkwrap_source_dir" to be set in setup() call.
    '''
    source_url = self.distribution.shrinkwrap_source_url
    source_dir = getattr(self.distribution, 'shrinkwrap_source_dir', None)

    self.download_and_unpack_tarball(source_url)
    if source_dir is None:
        # Remove .tar or .gz or .bz2 if present
        basename, ext = os.path.splitext(os.path.basename(source_url))
        while ext in ['.gz', '.bz2', '.tar']:
            basename, ext = os.path.splitext(basename)
        # Went one too far, now back up, ext could also be empty
        basename = basename + ext
        source_dir = basename

    os.chdir(source_dir)
    self.shell('./configure --prefix=' + self.virtualenv)
    self.make(extra_opts=['install'])


install_functions = { 'autoconf' : autoconf_install }
