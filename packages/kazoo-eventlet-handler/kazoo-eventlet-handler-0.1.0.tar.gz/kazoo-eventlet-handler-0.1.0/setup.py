__license__ = """
Copyright 2012 DISQUS

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
from setuptools import find_packages, setup

try:
    import multiprocessing
except ImportError:
    pass


install_requires = [
    'eventlet',
    'kazoo',
]

tests_require = [
    'mock',
    'nose',
]

setup_requires = []
if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')

setup(
    name='kazoo-eventlet-handler',
    version='0.1.0',
    author='ted kaemming, disqus',
    author_email='ted@disqus.com',
    url='http://github.com/disqus/kazoo-eventlet-handler',
    license='Apache License 2.0',
    packages=find_packages(exclude=('tests',)),
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    test_suite='nose.collector',
)
