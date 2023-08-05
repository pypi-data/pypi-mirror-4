# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, with_statement

import sys

import cuisine
from fabric.api import run as _run
from fabric.api import sudo as _sudo
from fabric.api import put as _put
from fabric.api import local, get, env

from revolver import contextmanager as _ctx
from revolver.decorator import inject_use_sudo

VERSION = '0.0.5'

env.sudo_forced = False
env.sudo_user = None


@inject_use_sudo
def put(*args, **kwargs):
    with _ctx.unpatched_state():
        return _put(*args, **kwargs)


def run(*args, **kwargs):
    if not env.sudo_forced:
        return _run(*args, **kwargs)

    return sudo(*args, **kwargs)


def sudo(*args, **kwargs):
    if env.sudo_user:
        kwargs['user'] = env.sudo_user

    return _sudo(*args, **kwargs)


# Monkeypatch sudo/run into fabric/cuisine
# TODO Added fabric.contrib.files because it was still wrong. Do we need to
#      patch even more places? Wrong import-order used? Investigate here!
from fabric.contrib import files as _files
for module in ("fabric.api", "fabric.contrib.files",
               "fabric.operations", "cuisine"):
    setattr(sys.modules[module], "run", run)
    setattr(sys.modules[module], "sudo", sudo)
