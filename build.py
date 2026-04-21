from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.coverage")
use_plugin("python.pylint")

name = "G87.2026.T10.GE2"
default_task = "publish"

@init
def set_properties(project):
    project.set_property("coverage_threshold_warn", 0)
    project.set_property("coverage_threshold_error", 0)
    project.set_property("coverage_break_build", False)
    project.set_property("pylint_options", ["--rcfile=pylintrc"])