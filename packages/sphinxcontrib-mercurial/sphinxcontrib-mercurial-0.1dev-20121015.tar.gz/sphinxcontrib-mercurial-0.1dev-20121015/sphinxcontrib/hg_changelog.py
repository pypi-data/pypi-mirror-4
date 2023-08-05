# -*- coding: utf-8-unix -*-
# Copyright 2012 (C) Takayuki KONDO <tkondou@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive

from mercurial import ui, hg, util


class HgChangeLog(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 4
    final_argument_whitespace = False
    option_spec = {
        'max_commits': directives.positive_int,
        'repo_root_path': directives.unchanged_required,
        'branch': directives.unchanged_required,
        'path': directives.unchanged_required
        }

    def run(self):
        repo_root_path = "."
        if 'repo_root_path' in self.options:
            repo_root_path = self.options['repo_root_path']

        repo = hg.repository(ui.ui(), repo_root_path)
        l = nodes.bullet_list()

        ctxes = self.get_ctxes(repo, self.options)

        for ctx in ctxes:
            item = nodes.list_item()
            item += [nodes.strong(text=ctx.description()),
                     nodes.inline(text=" by "),
                     nodes.emphasis(text=ctx.user()),
                     nodes.inline(text=" at "),
                     nodes.emphasis(text=util.datestr(ctx.date()))
                     ]
            l.append(item)
        return [l]

    def get_ctxes(self, repo, options):
        '''get suitable ctxes from commits'''
        max_commits = 10
        if 'max_commits' in options:
            max_commits = options['max_commits']
        branch = "default"
        if 'branch' in options:
            branch = options['branch']
        path = None
        if 'path' in options:
            path = options['path']

        commits = range(repo.changectx("tip").rev() + 1)
        commits.reverse()

        ret = []
        for commit in commits:
            if len(ret) >= max_commits:
                break
            ctx = repo.changectx(commit)
            if ctx.branch() != branch:
                continue
            if self.is_file_in_path(ctx.files(), path) is False:
                continue
            ret.append(ctx)

        return ret

    def is_file_in_path(self, files, path):
        '''Check files contain some file in specified path'''
        if path is None:
            return True
        for f in files:
            print f
            if f.startswith(path):
                return True
        return False


def setup(app):
    app.add_directive('hg_changelog', HgChangeLog)
