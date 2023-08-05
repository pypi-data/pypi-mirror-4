# -*- coding: utf-8 -*-
# Copyright (C)2012 'Biodec'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""Recipe for setting up Riak."""

import logging
import os
import pkg_resources
import shutil
import subprocess
import sys
import tempfile
import urllib
import zc.recipe.egg

logger = logging.getLogger(__name__)


class BuildRecipe(zc.recipe.egg.Eggs):
    """Buildout recipe for installing Riak."""

    def __init__(self, buildout, name, opts):
        """Standard constructor for zc.buildout recipes."""

        super(BuildRecipe, self).__init__(buildout, name, opts)
        self.options['location'] = os.path.join(
            self.buildout['buildout']['parts-directory'],
            self.name)

    def install_riak(self):
        """Downloads and installs Riak."""

        arch_filename = self.options['url'].split(os.sep)[-1]
        dst = self.options['location']
        # Re-use the buildout download cache if defined
        downloads_dir = self.buildout['buildout'].get('download-cache')
        if downloads_dir is None:
            downloads_dir = os.path.join(self.buildout['buildout']['directory'],
                                        'downloads')
            if not os.path.isdir(downloads_dir):
                os.mkdir(downloads_dir)
            self.buildout['buildout'].setdefault('download-cache', downloads_dir)
        logger.info("downloading Riak distribution... %r %r" % (downloads_dir, arch_filename))
        src = os.path.join(downloads_dir, arch_filename)
        if not os.path.isfile(src):
            logger.info("downloading Riak distribution...")
            urllib.urlretrieve(self.options['url'], src)
        else:
            logger.info("Riak distribution already downloaded.")

        extract_dir = tempfile.mkdtemp("buildout-" + self.name)
        remove_after_install = [extract_dir]
        is_ext = arch_filename.endswith
        is_archive = True
        if is_ext('.tar.gz') or is_ext('.tgz'):
            call = ['tar', 'xzf', src, '-C', extract_dir]
        elif is_ext('.zip'):
            call = ['unzip', src, '-d', extract_dir]
        else:
            is_archive = False

        if is_archive:
            retcode = subprocess.call(call)
            if retcode != 0:
                raise Exception("extraction of file %r failed (tempdir: %r)" %
                                (arch_filename, extract_dir))
        else:
            shutil.copy(arch_filename, extract_dir)

        if is_archive:
            top_level_contents = os.listdir(extract_dir)
            if len(top_level_contents) != 1:
                raise ValueError("can't strip top level directory because "
                                 "there is more than one element in the "
                                 "archive.")
            base = os.path.join(extract_dir, top_level_contents[0])
        else:
            base = extract_dir

        if not os.path.isdir(dst):
            os.mkdir(dst)

            for filename in os.listdir(base):
                shutil.move(os.path.join(base, filename),
                            os.path.join(dst, filename))
        else:
            logger.info("Riak already installed.")

        erlang_path = self.options.get('erlang-path')
        if erlang_path:
            new_path = [erlang_path] + os.environ['PATH'].split(':')
            os.environ['PATH'] = ':'.join(new_path)

        old_cwd = os.getcwd()
        os.chdir(dst)
        retcode = subprocess.call(['make', 'PYTHON=%s' % sys.executable])
        if retcode != 0:
            raise Exception("building Riak failed")
        os.chdir(old_cwd)
    
        for path in remove_after_install:
            shutil.rmtree(path)

        return [dst,]

    def install(self):
        """Creates the part."""

        return self.install_riak()

    def update(self):
        pass
