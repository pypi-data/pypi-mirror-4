# Software License Agreement (BSD License)
#
# Copyright (c) 2013, Open Source Robotics Foundation, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Open Source Robotics Foundation, Inc. nor
#    the names of its contributors may be used to endorse or promote
#    products derived from this software without specific prior
#    written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from catkin_pkg.package import parse_package_string


class DependencyWalker(object):

    ALL_DEPENDENCY_TYPES = ['buildtool', 'build', 'run', 'test']

    DIRECT_DEPENDS = {'buildtool': [], 'build': [], 'run': [], 'test': []}

    FULL_DEPENDS = {
        'buildtool': ALL_DEPENDENCY_TYPES,
        'build': ALL_DEPENDENCY_TYPES,
        'run': ALL_DEPENDENCY_TYPES,
        'test': ALL_DEPENDENCY_TYPES
    }

    def __init__(self, release_instance):
        self._release_instance = release_instance
        self._packages = {}
        self._dependency_cache = {
            'buildtool': {},
            'build': {},
            'run': {},
            'test': {}
        }

    def _get_package(self, pkg_name):
        if pkg_name not in self._packages:
            pkg_xml = self._release_instance.get_package_xml(pkg_name)
            pkg = parse_package_string(pkg_xml)
            self._packages[pkg_name] = pkg
        return self._packages[pkg_name]

    def get_depends(self, pkg_name, depend_type, ros_packages_only=False):
        '''Return the set of package dependencies of the specified type.'''
        deps = self._get_dependencies(pkg_name, depend_type)
        if ros_packages_only:
            deps = deps & set(self._release_instance.packages.keys())
        return deps

    def get_recursive_depends(self, pkg_name, depend_type, ros_packages_only=False):
        '''Return the set of recursive package dependencies of the specified type.'''
        if pkg_name not in self._dependency_cache[depend_type]:
            deps = self._get_dependencies(pkg_name, depend_type)
            for dep in sorted(deps):
                if dep not in self._release_instance.packages.keys():
                    continue
                rec_depends = self.get_recursive_depends(dep, depend_type)
                deps = deps | rec_depends
            self._dependency_cache[depend_type][pkg_name] = deps

        depends = self._dependency_cache[depend_type][pkg_name]
        if ros_packages_only:
            depends = depends & set(self._release_instance.packages.keys())
        return depends

    def get_recursive_depends2(self, pkg_name, depend_types, ros_packages_only=False):
        '''Return the set of recursive package dependencies of the specified types.'''
        depends = set([])
        for dep_type in sorted(depend_types):
            deps = self.get_recursive_depends(pkg_name, dep_type, ros_packages_only=ros_packages_only)
            depends = depends | deps
        return depends

    def get_mapped_depends(self, pkg_name, depend_walk, ros_packages_only=False):
        '''Return a dict mapping from dependency types to sets of (recursive) package dependencies specified by the walk-map.'''
        depends = {}
        for dep_type in sorted(depend_walk.keys()):
            deps = self._get_dependencies(pkg_name, dep_type)
            rec_deps = set([])
            for dep in sorted(deps):
                if dep not in self._release_instance.packages.keys():
                    continue
                x = self.get_recursive_depends2(dep, depend_walk[dep_type], ros_packages_only=ros_packages_only)
                rec_deps |= x
            if ros_packages_only:
                deps = deps & set(self._release_instance.packages.keys())
            depends[dep_type] = deps | rec_deps
        return depends

    def _get_dependencies(self, pkg_name, dep_type):
        assert dep_type in DependencyWalker.ALL_DEPENDENCY_TYPES
        pkg = self._get_package(pkg_name)
        deps = {
            'buildtool': pkg.buildtool_depends,
            'build': pkg.build_depends,
            'run': pkg.run_depends,
            'test': pkg.test_depends
        }
        return set([d.name for d in deps[dep_type]])
