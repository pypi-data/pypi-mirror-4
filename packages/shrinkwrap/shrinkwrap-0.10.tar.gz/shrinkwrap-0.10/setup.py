from setuptools import setup
from setuptools.command import install as _install
import os
import re

if 'VIRTUAL_ENV' not in os.environ:
    raise Exception('shrinkwrap can only be installed and run inside a Python virtualenv.')

from shrinkwrap import __version__

# From http://stackoverflow.com/questions/1446682/
class install(_install.install):
    def initialize_options(self):
        _install.install.initialize_options(self)

    def finalize_options(self):
        _install.install.finalize_options(self)

    def run(self):
        _install.install.run(self)

        # Create environment directory
        VIRTUAL_ENV = os.environ['VIRTUAL_ENV']
        env_dir = os.path.join(VIRTUAL_ENV, 'env.d')
        if not os.path.exists(env_dir):
            os.mkdir(env_dir)

        # Monkey-patch the virtualenv activate script
        activate = os.path.join(VIRTUAL_ENV, 'bin', 'activate')
        shrinkwrap_fragment = '''#begin shrinkwrap (DO NOT EDIT THIS SECTION)
eval $(shrinkwrap activate)
#end shrinkwrap'''
        with open(activate, 'r') as f:
            activate_contents = f.read()
        match = re.search(r'#begin shrinkwrap.*#end shrinkwrap', activate_contents, re.DOTALL)
        if match is not None:
            orig = match.group()
            new_activate_contents = activate_contents.replace(orig, shrinkwrap_fragment)
        else:
            new_activate_contents = activate_contents + '\n' + shrinkwrap_fragment + '\n'

        with open(activate, 'w') as f:
            f.write(new_activate_contents)
        print '%s/bin/activate has been updated' % VIRTUAL_ENV


setup(
    name='shrinkwrap',
    version=__version__,
    author='Stan Seibert',
    author_email='stan@mtrr.org',
    packages=['shrinkwrap'],
    url='http://bitbucket.org/seibert/shrinkwrap/',
    scripts=['bin/shrinkwrap'],
    license='LICENSE.txt',
    description='Helper modules for making wrapper packages around non-Python code.',
    long_description=open('README.txt').read(),
    entry_points = {
        "distutils.setup_keywords": [
            "shrinkwrap_source_url = shrinkwrap.install:assert_string",
            "shrinkwrap_source_dir = shrinkwrap.install:assert_string",
            "shrinkwrap_installer = shrinkwrap.install:validate_installer_option",
            "shrinkwrap_skip = shrinkwrap.install:assert_callable",
            "shrinkwrap_requires = setuptools.dist:assert_string_list",
        ],
    },
    cmdclass = {'install': install},
)
