#  This file is part of Python Builder
#
#  Copyright 2011-2013 PyBuilder Team
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import datetime
import optparse
import re
import sys
import traceback

from pybuilder import __version__
from pybuilder.core import Logger
from pybuilder.errors import PythonbuilderException
from pybuilder.execution import ExecutionManager
from pybuilder.reactor import Reactor
from pybuilder.terminal import BOLD, BROWN, RED, GREEN, bold, styled_text, fg, italic, \
    write, write_line, write_error, write_error_line, draw_line
from pybuilder.utils import format_timestamp

PROPERTY_OVERRIDE_PATTERN = re.compile(r'^[a-zA-Z0-9_]+=.*')

class CommandLineUsageException(PythonbuilderException):
    def __init__(self, usage, message):
        super(CommandLineUsageException, self).__init__(message)
        self.usage = usage


class StdOutLogger(Logger):
    def _level_to_string(self, level):
        if Logger.DEBUG == level:
            return "[DEBUG]"
        if Logger.INFO == level:
            return "[INFO] "
        if Logger.WARN == level:
            return "[WARN] "
        return "[ERROR]"

    def _do_log(self, level, message, *arguments):
        sys.stdout.write("%s %s\n" % (self._level_to_string(level), self._format_message(message, *arguments)))


class ColoredStdOutLogger(StdOutLogger):
    def _level_to_string(self, level):
        if Logger.DEBUG == level:
            return italic("[DEBUG]")
        if Logger.INFO == level:
            return bold("[INFO] ")
        if Logger.WARN == level:
            return styled_text("[WARN] ", BOLD, fg(BROWN))
        return styled_text("[ERROR]", BOLD, fg(RED))


def parse_options(args):
    parser = optparse.OptionParser(usage="%prog [options] task1 [[task2] ...]",
                                   version="%prog " + __version__)

    def error(msg):
        raise CommandLineUsageException(parser.get_usage() + parser.format_option_help(), msg)

    parser.error = error

    parser.add_option("-t", "--list-tasks",
                      action="store_true",
                      dest="list_tasks",
                      default=False,
                      help="List tasks")

    parser.add_option("-v", "--verbose",
                      action="store_true",
                      dest="verbose",
                      default=False,
                      help="Enable verbose output")

    project_group = optparse.OptionGroup(parser, "Project Options", "Customizes the project to build.")

    project_group.add_option("-D", "--project-directory",
                             dest="project_directory",
                             help="Root directory to execute in",
                             metavar="<project directory>",
                             default=".")
    project_group.add_option("-E", "--environment",
                             dest="environments",
                             help="Activate the given environment for this build. Can be used multiple times",
                             metavar="<environment>",
                             action="append",
                             default=[])
    project_group.add_option("-P",
                             action="append",
                             dest="property_overrides",
                             default=[],
                             metavar="<property>=<value>",
                             help="Set/ override a property value")

    parser.add_option_group(project_group)

    output_group = optparse.OptionGroup(parser, "Output Options", "Modifies the messages printed during a build.")

    output_group.add_option("-X", "--debug",
                            action="store_true",
                            dest="debug",
                            default=False,
                            help="Print debug messages")
    output_group.add_option("-q", "--quiet",
                            action="store_true",
                            dest="quiet",
                            default=False,
                            help="Quiet mode; print only warnings and errors")
    output_group.add_option("-Q", "--very-quiet",
                            action="store_true",
                            dest="very_quiet",
                            default=False,
                            help="Very quiet mode; print only errors")
    output_group.add_option("-C", "--no-color",
                            action="store_true",
                            dest="no_color",
                            default=False,
                            help="Disable colored output")

    parser.add_option_group(output_group)

    options, arguments = parser.parse_args(args=list(args))

    property_overrides = {}
    for pair in options.property_overrides:
        if not PROPERTY_OVERRIDE_PATTERN.match(pair):
            parser.error("%s is not a property definition." % pair)
        key, val = pair.split("=")
        property_overrides[key] = val

    options.property_overrides = property_overrides

    if options.very_quiet:
        options.quiet = True

    return options, arguments


def init_reactor(logger):
    execution_manager = ExecutionManager(logger)
    reactor = Reactor(logger, execution_manager)
    return reactor


def should_colorize(options):
    return sys.stdout.isatty() and not options.no_color


def init_logger(options):
    threshold = Logger.INFO
    if options.debug:
        threshold = Logger.DEBUG
    elif options.quiet:
        threshold = Logger.WARN

    if not should_colorize(options):
        logger = StdOutLogger(threshold)
    else:
        logger = ColoredStdOutLogger(threshold)

    return logger


def print_summary(successful, summary, start, end, options, failure_message):
    draw_line()
    if successful:
        msg = "BUILD SUCCESSFUL\n"
        if should_colorize(options):
            msg = styled_text(msg, BOLD, fg(GREEN))
    else:
        msg = "BUILD FAILED - %s\n" % failure_message
        if should_colorize(options):
            msg = styled_text(msg, BOLD, fg(RED))
    write(msg)
    draw_line()

    if successful and summary:
        write_line("Build Summary")
        write_line("%20s: %s" % ("Project", summary.project.name))
        write_line("%20s: %s" % ("Version", summary.project.version))
        write_line("%20s: %s" % ("Base directory", summary.project.basedir))
        write_line("%20s: %s" % ("Environments", ", ".join(options.environments)))

        task_summary = ""
        for task in summary.task_summaries:
            task_summary += " %s [%d ms]" % (task.task, task.execution_time)

        write_line("%20s:%s" % ("Tasks", task_summary))

    time_needed = end - start
    millis = ((time_needed.days * 24 * 60 * 60) + time_needed.seconds) * 1000 + time_needed.microseconds / 1000

    write_line("Build finished at %s" % format_timestamp(end))
    write_line("Build took %d seconds (%d ms)" % (time_needed.seconds, millis))

def main(*args):
    try:
        options, arguments = parse_options(args)
    except CommandLineUsageException as e:
        write_error_line("Usage error: %s\n" % e)
        write_error(e.usage)
        return 1

    start = datetime.datetime.now()

    logger = init_logger(options)
    reactor = init_reactor(logger)

    if options.list_tasks:
        reactor.prepare_build(property_overrides=options.property_overrides,
                              project_directory=options.project_directory)

        write_line("Tasks found in %s building in %s:" % (reactor.project.name, reactor.project.basedir))
        write_line()
        for task in sorted(reactor.get_tasks()):
            write_line("%20s\t%s" % (task.name, " ".join(task.description) or "<no description available>"))
            if task.dependencies:
                write_line("\t\t\tdepends on tasks: %s" % " ".join(task.dependencies))
            write_line()
        return 0

    banner = "PYBUILDER Version {0}".format(__version__)
    if should_colorize(options):
        banner = bold(banner)

    if not options.very_quiet:
        write_line(banner)
        write_line("Build started at %s" % format_timestamp(start))
        draw_line()

    successful = True
    failure_message = None
    summary = None

    try:
        try:
            reactor.prepare_build(property_overrides=options.property_overrides,
                                  project_directory=options.project_directory)

            if options.verbose:
                logger.debug("Verbose output enabled.\n")
                reactor.project.verbose = True

            if options.list_tasks:
                for task in sorted(reactor.get_tasks()):
                    write_line("%20s\t%s" % (task.name, task.description or "<no description available>"))
                    if task.dependencies:
                        write_line("\t\t\tdepends on tasks: %s" % " ".join(task.dependencies))
                    write_line()
            else:
                summary = reactor.build(environments=options.environments, tasks=arguments)

        except KeyboardInterrupt:
            raise PythonbuilderException("Build aborted")

    except Exception as e:
        failure_message = str(e)
        if options.debug:
            traceback.print_exc(file=sys.stderr)
        successful = False

    finally:
        end = datetime.datetime.now()
        if not options.very_quiet:
            print_summary(successful, summary, start, end, options, failure_message)

        if not successful:
            return 1

        return 0
