"""
    Copyright 2013 KU Leuven Research and Development - iMinds - Distrinet

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Administrative Contact: dnet-project-office@cs.kuleuven.be
    Technical Contact: bart.vanbrabant@cs.kuleuven.be
"""

from Imp.export import dependency_manager
from Imp.resources import Resource

@dependency_manager
def repo_before_package(model, resources):
    """
        If a yum repo is defined on a host, then make all package on that host depend on that repo
    """
    # loop over all resources to find files that where created from an instance of
    # yum::YumRepository
    for _id, resource in resources.items():
        res_class = resource.model.__class__
        if resource.model.__module__ == "yum" and res_class.__name__ == "YumRepository":
            model = resource.model
            host = model.host

            # now find all packages on the same host as the yum repo file and add the repo as a
            # dependency if it is not already a dependency
            for package in host.packages:
                pkg_res = Resource.get_resource(package)
                if pkg_res is not None:
                    if _id not in pkg_res.requires:
                        pkg_res.requires.add(_id)

