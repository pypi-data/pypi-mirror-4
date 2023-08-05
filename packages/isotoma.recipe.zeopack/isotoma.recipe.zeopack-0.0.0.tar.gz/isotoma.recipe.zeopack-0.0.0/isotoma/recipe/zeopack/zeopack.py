# Copyright 2012 Isotoma Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import sys
import os
import ConfigParser
import optparse

from ZEO.ClientStorage import ClientStorage
from ZEO.Exceptions import ClientDisconnected

logger = logging.getLogger(__name__)


class Storage(object):
    def __init__(self, storage, location, addr, username=None, password=None, realm=None, blob_dir=None, shared_blob_dir=True):
        self.storage = storage
        self.location = location
        self.addr = addr
        self.username = username
        self.password = password
        self.realm = realm
        self.blob_dir = blob_dir
        self.shared_blob_dir = shared_blob_dir

    def get_storage(self):
        kwargs = {}

        kwargs['storage'] = self.storage
        kwargs['wait'] = False
        kwargs['read_only'] = True
        if self.username:
            kwargs['username'] = self.username
        if self.password:
            kwargs['password'] = self.password
        if self.realm:
            kwargs['realm'] = self.realm
        try:
            from ZODB.interfaces import IBlobStorage
            if self.blob_dir:
                kwargs['blob_dir'] = os.path.abspath(self.blob_dir)
                kwargs['shared_blob_dir'] = self.shared_blob_dir
        except ImportError:
            pass
        return ClientStorage(self.addr, **kwargs)

    def rotate_once(self, old_path, new_path):
        if os.path.exists(old_path):
            logger.debug("Rotating %s to %s" % (os.path.basename(old_path), os.path.basename(new_path)))
            os.rename(old_path, new_path)

    def rotate(self, days):
        if days <= 1:
            logger.debug("Not keeping enough backups to need to rotate")
            return

        if not os.path.exists(self.location + ".tmp"):
            logger.debug("No existing backup so not rotating")
            return

        for i in range(days-2, -1, -1):
            self.rotate_once("%s.%s" % (self.location, i), "%s.%s" % (self.location, i+1))

        self.rotate_once(self.location + ".tmp", self.location + ".1")

    def pack(self, gc_days=7, backup_days=1):
        logger.info("Starting to pack %s" % self.location)

        cs = self.get_storage()

        if not cs.is_connected():
            logger.error("Zeoserver disconnected (not running?). Not packing.")
            sys.exit(1)

        self.rotate(backup_days)

        try:
            cs.pack(wait=True, days=gc_days)
        except ClientDisconnected:
            logger.error("Zeoserver disconnected whilst trying to pack. Not packing.")
            sys.exit(1)

        cs.close()


def main(config):
    p = optparse.OptionParser()
    p.add_option("-v", "--verbose", action="count")
    p.add_option("-d", "--debug", action="store_true")
    opts, args = p.parse_args()

    log_level = logging.WARNING
    if opts.verbose == 1:
        log_level = logging.INFO
    elif opts.verbose >= 2:
        log_level = logging.DEBUG

    logging.basicConfig(level=log_level)
    if not opts.debug:
        logging.getLogger().setLevel(logging.ERROR)
        logger.setLevel(log_level)

    p = ConfigParser.ConfigParser()
    p.read(config)

    if not p.has_section("zeopack"):
        logger.error("[%s] No [zeopack] section found in configuration" % config)
        sys.exit(1)

    if p.has_option("zeopack", "unix"):
        addr = p.get("zeopack", "unix")
    elif p.has_option("zeopack", "port"):
        host = p.get("zeopack", "host")
        port = p.get("zeopack", "port")
        addr = host, int(port)
    else:
        logger.error("[%s] Must specify unix socket or port" % config)
        sys.exit(1)

    if not p.has_option("zeopack", "storages"):
        logger.error("[%s] Must specify list of storages" % config)
        sys.exit(1)

    for storage in p.get("zeopack", "storages").strip().split("\n"):
        if not storage:
            # ignore blank lines
            continue

        if not p.has_section(storage):
            logger.error("[%s] Missing section '%s'" % (config, storage))
            sys.exit(1)

        section = dict(p.items(storage))
        name = section.get("name", storage)

        for key in ("location", "gc", "rotation"):
            if not key in section:
                logger.error("[%s] Missing '%s' in section '%s'" % (config, key, storage))
                sys.exit(1)

        s = Storage(name, section["location"], addr,
            username=section.get("username", None),
            password=section.get("password", None),
            realm=section.get("realm", None),
            blob_dir=section.get("blob_dir", None),
            shared_blob_dir=section.get("shared_blob_dir", "true").lower() in ("yes", "true", "on", "1"),
            )

        s.pack(int(section["gc"]), int(section["rotation"]))

