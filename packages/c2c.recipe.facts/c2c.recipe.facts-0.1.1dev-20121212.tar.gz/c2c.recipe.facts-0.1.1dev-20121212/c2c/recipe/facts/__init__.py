# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE


class Facts(object):

    def __init__(self, buildout, name, options):
        p = Popen(['facter'], stdout=PIPE)
        p.wait()
        for line in p.stdout.readlines():
            k, v = line.split(' => ')
            options[k] = v.strip()

    def install(self):
        return ()

    update = install
