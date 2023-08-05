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

import logging
import os

from django.conf import ENVIRONMENT_VARIABLE, Settings, settings
from django.core.exceptions import ImproperlyConfigured
from kazoo.client import KazooClient

from menagerie.holder import ZooKeeperSettingsHolder


logger = logging.getLogger(__name__)


def configure(module=None, client=KazooClient, holder=ZooKeeperSettingsHolder):
    if module is None:
        try:
            module = os.environ[ENVIRONMENT_VARIABLE]
            if not module:
                raise KeyError
        except KeyError:
            raise ImproperlyConfigured('%s is not defined, cannot import settings')

    __settings = Settings(module)

    hosts = ','.join(__settings.ZOOKEEPER_HOSTS)
    if hasattr(__settings, 'ZOOKEEPER_SETTINGS_NAMESPACE'):
        hosts = '/'.join((hosts, __settings.ZOOKEEPER_SETTINGS_NAMESPACE))

    logger.debug('Attempting to connect to ZooKeeper at "%s"...', hosts)
    zookeeper = client(hosts=hosts)
    zookeeper.start()

    settings.configure(holder(zookeeper, defaults=__settings))
