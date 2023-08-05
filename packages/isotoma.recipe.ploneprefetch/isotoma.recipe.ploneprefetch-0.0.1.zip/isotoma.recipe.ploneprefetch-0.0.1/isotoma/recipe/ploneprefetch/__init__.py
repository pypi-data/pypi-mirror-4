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


import os
import sys
import glob
import tarfile
from zc.buildout.download import Download


class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

        buildout = self.buildout['buildout']

        # If no URL is specified then don't do anything
        if not self.options.get("url", None):
            return

        # If a python version is specified then make sure that is the version
        # of python we are currently using. There is no point fetching 60mb+ of
        # Plone if its for a different python version!
        python_ver = self.options.get("python", None)
        if python_ver:
            current_ver = "%s.%s" % sys.version_info[:2]
            if python_ver != current_ver:
                return

	# Only way we can tell if we already ran is to look for a Plone egg in
	# the eggs-directory
        if glob.glob(os.path.join(buildout['eggs-directory'], "Plone-*.egg")):
            return

        print "Attempting to fetch Plone from: %s" % self.options["url"]

        # Download the unified installer with the buildout download abstraction
        # Respects the download cache (if there is one)
	# When used in conjuction with isotoma.buildout.basicauth, supports
	# basic auth and retrying on failure.
        download = Download(
            cache = buildout.get("download-cache", None),
            )
        path, is_temp = download(self.options["url"])

        # Open the outer .tar.gz and find the inner .tar.bz2
        print "Preparing to extract..."
        installer = tarfile.open(path)
        buildout_cache = tarfile.open(fileobj=installer.extractfile("%s/packages/buildout-cache.tar.bz2" % installer.next().name))

        eggs_directory = buildout['eggs-directory']
        downloads_directory = buildout.get("download-cache", None)

	# Extract all the things - send downloads into
	# ${buildout:download-cache} and eggs into ${buildout:eggs-directory}
        print "Extracting..."
        for f in buildout_cache:
            dest = None

            if downloads_directory and f.name.startswith("buildout-cache/downloads/"):
                dest = os.path.join(downloads_directory, f.name[25:])
            elif f.name.startswith("buildout-cache/eggs/"):
                dest = os.path.join(eggs_directory, f.name[20:])

            if not dest or os.path.exists(dest):
                continue

            buildout_cache.extract(f, dest)

	# If user isnt setting ${buildout:download-cache} then we'l have to
	# clean up the temporary download file
        if is_temp:
            os.unlink(path)

    def install(self):
        return []

    update = install

