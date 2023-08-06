import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'etsmtl'))
import version

path, script = os.path.split(sys.argv[0])
os.chdir(os.path.abspath(path))

install_requires = ['requests >= 0.8.8', 'simplejson']

try:
    import json
    _json_loaded = hasattr(json, 'loads')
except ImportError:
    pass

setup(name='etsmtl',
      version=version.VERSION,
      description='ETSMTL python bindings',
      packages=['etsmtl'],
      package_data={'etsmtl': ['data/ca-certificates.crt', '../VERSION']},
      install_requires=install_requires,
      )
