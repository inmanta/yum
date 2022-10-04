"""
    Copyright 2020 Inmanta

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Contact: code@inmanta.com
"""
import pytest
from pytest_inmanta.plugin import Project
from inmanta.ast import CompilerException


def test_module(project: Project) -> None:
    project.compile("import yum")


def test_input_validation_on_repository(project: Project):
    """
    Verify that an exception is raised when the baseurl and the mirrorlist of
    a Repository is set to null.
    """
    with pytest.raises(CompilerException) as excinfo:
        project.compile("""
    import yum
    yum::Repository(name="test")
        """)
    assert "baseurl and mirrorlist cannot be null at the same time." in str(excinfo.value)


def test_repository(project: Project):
    """
    Basic test for the Repository entity.
    """
    project.compile("""
import std
import yum
import redhat
host= std::Host(name="localhost", os=redhat::rocky8)
yum::Repository(
    host=host,
    name="test",
    gpgcheck=true,
    enabled=true,
    baseurl="http://baseurl.com",
    mirrorlist="http://mirror.com",
    gpgkey="http://gpgkey.com",
    metadata_expire=7200,
    skip_if_unavailable=false,
)
    """)

    file_instances = project.get_instances(fortype="std::File")
    assert len(file_instances) == 1
    expected_content_repo_file = """
[test]
name = test
enabled=1
gpgcheck=1
baseurl = http://baseurl.com
mirrorlist = http://mirror.com
gpgkey = http://gpgkey.com
metadata_expire = 7200
skip_if_unavailable=0
    """.strip()
    assert file_instances[0].content.strip() == expected_content_repo_file
    assert file_instances[0].path == "/etc/yum.repos.d/test.repo"
