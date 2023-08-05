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
"""Config Recipe riak"""
import os
import subprocess
import logging

RECIPE_BUILD_NAME = 'biodec.recipe.riak:build'


def get_options_from_build(buildout, options):
    part = options.get('riakbuildpart', None)
    if part:
        return buildout[part]

    for part in buildout.keys():
        if 'recipe' in buildout[part] and \
                buildout[part]['recipe'] == RECIPE_BUILD_NAME:
            return buildout[part]
    return {}


class InstanceRecipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        location = options.get(
            'location', buildout['buildout']['parts-directory'])
        print location
        options['location'] = os.path.join(location, name)
        options['prefix'] = options['location']

        self.options = options
        self.buildoptions = get_options_from_build(buildout, options)
        self.logger = logging.getLogger(__name__)

    def gen_scripts(self, target_dir):
        """Generates Riak bin scripts."""
        bindir = self.buildout['buildout']['bin-directory']

        erlang_path = self.options.get('erlang-path')
        if erlang_path:
            erlang_path = 'PATH=%s:$PATH' % erlang_path
        else:
            erlang_path = ''
        scripts = []
        for scriptname in ('riak', 'riak-admin', 'search-cmd'):
            script = os.path.join(bindir, "%s.%s" % (self.name, scriptname))
            f = open(script, 'wb')
            f.write('#!/usr/bin/env bash\n%s\ncd %s\nexec bin/%s $@\n' %
                    (erlang_path, target_dir, scriptname))
            print erlang_path, target_dir, scriptname
            f.close()
            os.chmod(script, 0755)
            scripts.append(script)
        return scripts

    def install(self):
        """ install riak instance """
        dst = self.options.setdefault(
            'location',
            os.path.join(self.buildout['buildout']['parts-directory'],
                         self.name))
        print 'dst', dst
        if not os.path.isdir(dst):
            os.mkdir(dst)
        var = os.path.join(
            self.buildout['buildout']['directory'],
            'var', self.name)
        print 'var', var
        if not os.path.isdir(var):
            os.mkdir(var)
        target_dir = os.path.join(dst, 'rel')
        overlay_vars = os.path.join(dst, 'vars.config')
        open(overlay_vars, 'w').write(CONFIG_TEMPLATE % dict(
            root=target_dir,
            var=var,
            web_ip=self.options.get('web_ip', '127.0.0.1'),
            web_port=self.options.get('web_port', 8098)
        ))
        old_cwd = os.getcwd()
        os.chdir(self.buildoptions['location'])
        my_env = os.environ.copy()
        if self.buildoptions.get('erlang-path'):
            my_env["PATH"] = "%s:%s" % (
                self.buildoptions.get('erlang-path'), my_env.get("PATH"))
        retcode = subprocess.Popen(
            ['./rebar', 'generate',
             'target_dir=%s' % target_dir, 'overlay_vars=%s' % overlay_vars],
            env=my_env).wait()
        if retcode != 0:
            raise Exception("Creating Riak instance %s" % self.name)
        os.chdir(old_cwd)

        scripts = self.gen_scripts(target_dir)
        return [dst, ] + scripts

    def update(self):
        """ update riak instance """
        self.logger.warning('not implemented')


CONFIG_TEMPLATE = '''
%%%% -*- mode: erlang;erlang-indent-level: 4;indent-tabs-mode: nil -*-
%%%% ex: ft=erlang ts=4 sw=4 et

%%%% Platform-specific installation paths
{platform_bin_dir,  "%(root)s/bin"}.
{platform_data_dir, "%(var)s/data"}.
{platform_etc_dir,  "%(root)s/etc"}.
{platform_lib_dir,  "%(root)s/lib"}.
{platform_log_dir,  "%(var)s/log"}.

%%%%
%%%% etc/app.config
%%%%
{web_ip,            "%(web_ip)s"}.
{web_port,          %(web_port)s}.
{handoff_port,      8099}.
{pb_ip,             "127.0.0.1"}.
{pb_port,           8087}.
{ring_state_dir,    "{{platform_data_dir}}/ring"}.
{bitcask_data_root, "{{platform_data_dir}}/bitcask"}.
{leveldb_data_root, "{{platform_data_dir}}/leveldb"}.
{sasl_error_log,    "{{platform_log_dir}}/sasl-error.log"}.
{sasl_log_dir,      "{{platform_log_dir}}/sasl"}.
{mapred_queue_dir,  "{{platform_data_dir}}/mr_queue"}.

%%%% riak_search
{merge_index_data_root,  "{{platform_data_dir}}/merge_index"}.

%%%% secondary indices
{merge_index_data_root_2i,  "{{platform_data_dir}}/merge_index_2i"}.

%%%% Javascript VMs
{map_js_vms,   8}.
{reduce_js_vms, 6}.
{hook_js_vms, 2}.

%%%%
%%%% etc/vm.args
%%%%
{node,         "riak@127.0.0.1"}.
{crash_dump,   "{{platform_log_dir}}/erl_crash.dump"}.

%%%%
%%%% bin/riak
%%%%
{runner_script_dir,  "$(cd ${0%%/*} && pwd)"}.
{runner_base_dir,    "${RUNNER_SCRIPT_DIR%%/*}"}.
{runner_etc_dir,     "$RUNNER_BASE_DIR/etc"}.
{runner_log_dir,     "{{platform_log_dir}}"}.
{pipe_dir,           "%(var)s/tmp/"}.
{runner_user,        ""}.
'''
