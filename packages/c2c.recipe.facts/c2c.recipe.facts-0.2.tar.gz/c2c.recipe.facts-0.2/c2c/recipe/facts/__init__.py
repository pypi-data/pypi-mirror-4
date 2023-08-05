# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE
from os import environ


class Facts(object):

    def __init__(self, buildout, name, options):
        env = environ
        if 'PATH' not in env:
            env = env.copy()
            env['PATH'] = '/usr/bin:/bin'

        p = Popen(['facter'], stdout=PIPE, env=env)
        p.wait()
        for line in p.stdout.readlines():
            k, v = line.split(' => ')
            options[k] = v.strip()

    def install(self):
        return ()

    update = install
