# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, with_statement

from cuisine import file_attribs as attributes
from cuisine import file_attribs_get as attributes_get
from cuisine import file_ensure as ensure
from cuisine import file_is_file as exists
from cuisine import file_is_link as is_link
from cuisine import file_link as link
from cuisine import file_local_read as read_local
from cuisine import file_read as read
from cuisine import file_update as update
from cuisine import file_write as write
from fabric.contrib.files import append, comment, contains, sed, uncomment

from revolver import core
from revolver.decorator import inject_use_sudo

append = inject_use_sudo(append)
comment = inject_use_sudo(comment)
contains = inject_use_sudo(contains)
sed = inject_use_sudo(sed)
uncomment = inject_use_sudo(uncomment)
write = inject_use_sudo(write)


def temp(mode=None, owner=None, group=None):
    path = core.run('mktemp').stdout
    attributes(path, mode=mode, owner=owner, group=group)
    return path


def remove(location, recursive=False, force=True):
    force = force and '-f' or ''
    recursive = recursive and '-r' or ''

    core.run('rm %s %s %s' % (force, recursive, location))


def touch(location, mode=None, owner=None, group=None):
    core.run('touch %s' % location)
    attributes(location, mode=mode, owner=owner, group=group)


def copy(source, destination, force=True, mode=None, owner=None, group=None):
    force = force and '-f' or ''

    core.run('cp %s %s %s' % (force, source, destination))
    attributes(destination, mode=mode, owner=owner, group=group)
