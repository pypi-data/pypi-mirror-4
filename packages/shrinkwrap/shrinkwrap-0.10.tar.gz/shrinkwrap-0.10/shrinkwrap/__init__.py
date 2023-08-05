__version__ = '0.10'

# Require a virtual environment to use shrinkwrap
import os
if 'VIRTUAL_ENV' not in os.environ:
    raise ImportError('shrinkwrap can only be used inside a virtualenv.')
