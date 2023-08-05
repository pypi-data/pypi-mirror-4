# -*- coding: utf-8-unix -*-
# Copyright 2012 (C) Takayuki KONDO <tkondou@gmail.com>
#
import sys
import os, subprocess

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive


if sys.version_info[0] >= 3:
    def b(s):
        '''A helper function to emulate 2.6+ bytes literals using string
        literals.'''
        return s.encode('latin1')
else:
    def b(s):
        '''A helper function to emulate 2.6+ bytes literals using string
        literals.'''
        return s

class HgVersion(Directive):

    def runcmd(self, cmd, env):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=env)
        out, err = p.communicate()
        return out, err

    def runhg(self, cmd, env):
        out, err = self.runcmd(cmd, env)

        err = [e for e in err.splitlines()
               if not e.startswith(b('Not trusting file')) \
               and not e.startswith(b('warning: Not importing'))]
        if err:
            return ''
        return out

    def run(self):
        env = {'LANGUAGE': 'C'}
        cmd = ['hg', 'log', '-r', '.', '--template', '{tags}\n']
        numerictags = [t for t in self.runhg(cmd, env).split() if t[0].isdigit()]
        hgid = self.runhg(['hg', 'id', '-i', '-t'], env).strip()

        version = ''

        if numerictags: # tag(s) found
            version = numerictags[-1]
            if hgid.endswith('+'): # propagate the dirty status to the tag
                version += '+'
        else: # no tag found
            cmd = [sys.executable, 'hg', 'parents', '--template',
                   '{latesttag}+{latesttagdistance}-']
            version = self.runhg(cmd, env) + hgid
            if version.endswith('+'):
                version += time.strftime('%Y%m%d')

        l = nodes.bullet_list()
        item = nodes.list_item()
        item += [nodes.inline(text=version)]
        l.append(item)

        return [l]

