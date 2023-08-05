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

import sys
import os
import ConfigParser
import zc.buildout


class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout, self.options, self.name = buildout, options, name

    def install(self):
        extra_paths = self.options.get("extra-paths", [])

        zeoserver = self.buildout[self.options["zeoserver"]]

	# For Zope 2.10 and below we don't have eggs. The Zope 2.10 version of
	# the zeoserver recipe will tell us where the un-egged zope is via its
	# 'zope2-location' parameter
        if "zope2-location" in zeoserver:
            extra_paths.append(zeoserver["zope2-location"])

        p = ConfigParser.ConfigParser()

        p.add_section("zeopack")

        zeo_address = zeoserver.get("zeo-address", "8100")
        if ":" in zeo_address:
            host, port = zeo_address.split(":")
        else:
            host, port = "localhost", zeo_address
        p.set("zeopack", "host", host)
        p.set("zeopack", "port", port)

        p.add_section("main")
        p.set("main", "name", zeoserver.get("storage-number", "1"))
        p.set("main", "location", zeoserver.get("file-storage", os.path.join(self.buildout['buildout']['directory'], "var/filestorage/Data.fs")))
        if "blob-storage" in zeoserver:
            p.set("main", "blob_dir", zeoserver.get("blob-storage", None))
        if "pack-user" in zeoserver:
            p.set("main", "username", zeoserver["pack-user"])
        if "pack-password" in zeoserver:
            p.set("main", "password", zeoserver["pack-password"])
        if "authentication-realm" in zeoserver:
            p.set("main", "realm", zeoserver["authentication-realm"])
        p.set("main", "gc", zeoserver.get("pack-days", "1"))
        p.set("main", "rotation", zeoserver.get("pack-rotate-days", "1"))

        storages = ["main"]

        if "filestorage" in self.options:
            filestorage_name = self.options["filestorage"]
            filestorage = self.buildout[filestorage_name]

            parts = filestorage.get("parts", "").strip().split("\n")
            for part_name in parts:
                if not part_name:
                    continue
                part = self.buildout[filestorage_name + "_" + part_name]

                p.add_section(part_name)
                p.set(part_name, "name", part.get("zeo-storage", part_name))
                p.set(part_name, "location", part.get("location", os.path.join(self.buildout['buildout']['directory'], "var/filestorage/%s.Data.fs" % part_name)))
                if "zeo-blob-storage" in part:
                    p.set(part_name, "blob_dir", part["zeo-blob-storage"])
                if "pack-user" in zeoserver:
                    p.set(part_name, "username", zeoserver["pack-user"])
                if "pack-password" in zeoserver:
                    p.set(part_name, "password", zeoserver["pack-password"])
                if "authentication-realm" in zeoserver:
                    p.set(part_name, "realm", zeoserver["authentication-realm"])
                p.set(part_name, "gc", part.get("pack-days", zeoserver.get("pack-days", "1")))
                p.set(part_name, "rotation", part.get("pack-rotate-days", zeoserver.get("pack-rotate-days", "1")))
 
            storages.append(part_name)

        p.set("zeopack", "storages", "\n".join(storages))

        outputdir = os.path.join(self.buildout["buildout"]["parts-directory"], self.name)
        configpath = os.path.join(outputdir, "zeopack.cfg")
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        self.options.created(outputdir)

        fp = open(configpath, "w")
        p.write(fp)
        fp.close()
        self.options.created(configpath)

        path = self.buildout["buildout"]["bin-directory"]
        egg_paths = [
            self.buildout["buildout"]["develop-eggs-directory"],
            self.buildout["buildout"]["eggs-directory"],
            ]
        arguments = "'%s'" % self

        ws = zc.buildout.easy_install.working_set(["isotoma.recipe.zeopack", zeoserver["recipe"]], sys.executable, egg_paths)

        zc.buildout.easy_install.scripts(
            [('zeopack', 'isotoma.recipe.zeopack.zeopack', 'main')],
            ws,
            sys.executable,
            self.buildout['buildout']['bin-directory'],
            arguments="'%s'" % configpath,
            extra_paths=extra_paths,
            )

        return self.options.created()

