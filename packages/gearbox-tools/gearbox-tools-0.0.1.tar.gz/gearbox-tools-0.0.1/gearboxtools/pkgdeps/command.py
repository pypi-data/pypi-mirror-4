from __future__ import print_function

import os
import pkg_resources
from pip.log import logger
from pip.index import PackageFinder
from pip.req import RequirementSet, InstallRequirement
from pip.locations import build_prefix, src_prefix

from cliff.lister import Lister

class PackageDepsCommand(Lister):
    def get_description(self):
        return 'Shows full list of package dependencies'

    def get_parser(self, prog_name):
        parser = super(PackageDepsCommand, self).get_parser(prog_name)

        parser.add_argument('package', nargs=1)

        return parser

    def take_action(self, opts):
        pkg = opts.package[0]

        deps = self._get_dependencies(pkg)
        grouped_deps = {}
        for pair in deps:
            dep = pair[1]
            grouped_deps[dep.req.key] = dep.req

        return (('Package',),
                [[str(d)] for d in grouped_deps.values()])

    def _trace_dependencies(self, req, requirementSet, dependencies, _visited=None):
        _visited = _visited or set()
        if req in _visited:
            return
        _visited.add(req)
        for reqName in req.requirements():
            try:
                name = pkg_resources.Requirement.parse(reqName).project_name
            except ValueError as e:
                logger.error('Invalid requirement: %r (%s) in requirement %s' % (reqName, e, req))
                continue

            subreq = requirementSet.get_requirement(name)
            dependencies.append((req, subreq))
            self._trace_dependencies(subreq, requirementSet, dependencies, _visited)

    def _get_dependencies(self, name, requirementSet=None, finder=None):
        if requirementSet is None:
            requirementSet = RequirementSet(
                build_dir=os.path.abspath(build_prefix),
                src_dir=os.path.abspath(src_prefix),
                download_dir=None,
                download_cache=None,
                upgrade=False,
                ignore_installed=False,
                ignore_dependencies=False)

        if finder is None:
            finder = PackageFinder(find_links=[],
                index_urls=['http://pypi.python.org/simple'])

        # lead pip download all dependencies
        req = InstallRequirement.from_line(name, None)
        requirementSet.add_requirement(req)
        requirementSet.prepare_files(finder)

        # trace the dependencies relationships between projects
        dependencies = []
        self._trace_dependencies(req, requirementSet, dependencies)
        return dependencies
