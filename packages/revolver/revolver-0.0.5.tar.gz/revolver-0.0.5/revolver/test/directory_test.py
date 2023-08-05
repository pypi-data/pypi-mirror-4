# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, with_statement

from fudge import patch
import cuisine

from revolver import directory

from .utils import run_result


def test_revolver_is_just_a_wrapper():
    assert directory.attributes == cuisine.dir_attribs
    assert directory.attributes_get == cuisine.file_attribs_get
    assert directory.ensure == cuisine.dir_ensure
    assert directory.exists == cuisine.dir_exists
    assert directory.is_link == cuisine.file_is_link


@patch("revolver.directory.mkdtemp")
def test_temp_local(mkdtemp):
    mkdtemp.expects_call().returns(run_result("path"))
    assert directory.temp_local() == "path"


@patch("revolver.core.run")
@patch("revolver.directory.attributes")
def test_temp_calles_mktemp(run, attributes):
    (run.expects_call()
        .with_args("mktemp --directory")
        .returns(run_result("foo")))
    attributes.expects_call()
    assert directory.temp() == "foo"


@patch("revolver.core.run")
@patch("revolver.directory.attributes")
def test_temp_default_attributes(run, attributes):
    run.expects_call().returns(run_result("path"))
    (attributes.expects_call()
        .with_args("path", mode=None, owner=None, group=None))
    directory.temp()


@patch("revolver.core.run")
@patch("revolver.directory.attributes")
def test_temp_passes_attributes(run, attributes):
    run.expects_call().returns(run_result("path"))
    (attributes.expects_call()
        .with_args("path", mode="foo", owner="bar", group="baz"))
    directory.temp("foo", "bar", "baz")


@patch("revolver.core.run")
def test_remove_defaults(run):
    run.expects_call().with_args("rm -f  path")
    directory.remove("path")


@patch("revolver.core.run")
def test_remove_recusrive(run):
    run.expects_call().with_args("rm -f  path")
    directory.remove("path", recursive=False)

    run.expects_call().with_args("rm -f -r path")
    directory.remove("path", recursive=True)


@patch("revolver.core.run")
def test_remove_force(run):
    run.expects_call().with_args("rm   path")
    directory.remove("path", force=False)

    run.expects_call().with_args("rm -f  path")
    directory.remove("path", force=True)


@patch("revolver.core.run")
@patch("revolver.directory.exists")
def test_create_if_path_exists(run, exists):
    exists.expects_call().with_args("path").returns(True)
    directory.create("path")


@patch("revolver.core.run")
@patch("revolver.directory.exists")
def test_create_defaults(run, exists):
    exists.expects_call().with_args("path").returns(False)
    run.expects_call().with_args("mkdir  path")
    directory.create("path")


@patch("revolver.core.run")
@patch("revolver.directory.exists")
def test_create_recursive(run, exists):
    exists.expects_call().returns(False)
    run.expects_call().with_args("mkdir -p path")
    directory.create("path", recursive=True)


@patch("revolver.core.run")
@patch("revolver.directory.exists")
@patch("revolver.directory.attributes")
def test_create_default_attributes(run, exists, attributes):
    run.expects_call().with_args("mkdir  path")
    exists.expects_call().returns(False)
    (attributes.expects_call()
        .with_args("path", mode=None, owner=None, group=None))
    directory.create("path")


@patch("revolver.core.run")
@patch("revolver.directory.exists")
@patch("revolver.directory.attributes")
def test_create_passes_attributes(run, exists, attributes):
    run.expects_call().with_args("mkdir  path")
    exists.expects_call().returns(False)
    (attributes.expects_call()
        .with_args("path", mode="foo", owner="bar", group="baz"))
    directory.create("path", mode="foo", owner="bar", group="baz")
