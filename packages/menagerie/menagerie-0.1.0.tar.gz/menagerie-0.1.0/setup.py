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
    import multiprocessing  # noqa
except ImportError:
    pass


install_requires = [
    'Django>=1.2,<1.5',
    'kazoo>=0.5,<0.9',
]

tests_require = [
    'exam==0.4.2',
    'nose',
    'unittest2',
]

setup_requires = []
if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')

setup(
    name='menagerie',
    version='0.1.0',
    url='http://github.com/disqus/menagerie',
    author='ted kaemming, disqus',
    author_email='ted@disqus.com',
    packages=find_packages(exclude=('tests',)),
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    test_suite='nose.collector',
    license='Apache License 2.0',
    zip_safe=False,
)
