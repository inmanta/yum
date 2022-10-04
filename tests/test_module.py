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
from inmanta.ast import CompilerException
from pytest_inmanta.plugin import Project


def test_module(project: Project) -> None:
    project.compile("import yum")


def test_input_validation_on_repository(project: Project):
    """
    Verify that an exception is raised when the baseurl, mirrorlist and metalink attributes of
    a Repository are set to null.
    """
    with pytest.raises(CompilerException) as excinfo:
        project.compile(
            """
    import yum
    yum::Repository(name="test")
        """
        )
    assert "baseurl, mirrorlist and metalink cannot be null at the same time." in str(
        excinfo.value
    )


@pytest.mark.parametrize("baseurl", [True, False])
@pytest.mark.parametrize("mirrorlist", [True, False])
@pytest.mark.parametrize("metalink", [True, False])
def test_repository(project: Project, baseurl: bool, mirrorlist: bool, metalink: bool):
    """
    Basic test for the Repository entity.
    """
    if not baseurl and not mirrorlist and not metalink:
        # This combination is tested in test case: test_input_validation_on_repository
        return
    project.compile(
        f"""
import std
import yum
import redhat
host= std::Host(name="localhost", os=redhat::rocky8)
yum::Repository(
    host=host,
    name="test",
    gpgcheck=true,
    enabled=true,
    baseurl={"'http://baseurl.com'" if baseurl else "null"},
    mirrorlist={"'http://mirror.com'" if mirrorlist else "null"},
    metalink={"'http://metalink.com'" if metalink else "null"},
    gpgkey="http://gpgkey.com",
    metadata_expire=7200,
    skip_if_unavailable=false,
)
    """
    )

    def get_expected_config_file() -> str:
        result = """
[test]
name = test
enabled=1
gpgcheck=1
        """.strip()
        if baseurl:
            result = f"{result}\nbaseurl = http://baseurl.com"
        if mirrorlist:
            result = f"{result}\nmirrorlist = http://mirror.com"
        if metalink:
            result = f"{result}\nmetalink = http://metalink.com"
        return (
            result
            + "\n"
            + """
gpgkey = http://gpgkey.com
metadata_expire = 7200
skip_if_unavailable=0
        """.strip()
        )

    file_instances = project.get_instances(fortype="std::File")
    assert len(file_instances) == 1
    assert file_instances[0].content.strip() == get_expected_config_file()
    assert file_instances[0].path == "/etc/yum.repos.d/test.repo"
