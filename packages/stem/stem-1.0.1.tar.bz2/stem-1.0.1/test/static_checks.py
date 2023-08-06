# Copyright 2012-2013, Damian Johnson
# See LICENSE for licensing information

"""
Performs a check that our python source code follows its whitespace conventions
which are...

* two space indentations
* tabs are the root of all evil and should be shot on sight
* standard newlines (\\n), not windows (\\r\\n) nor classic mac (\\r)
"""

import re
import os

from stem.util import conf, system

# if ran directly then run over everything one level up
DEFAULT_TARGET = os.path.sep.join(__file__.split(os.path.sep)[:-1])

# mapping of files to the issues that should be ignored
PYFLAKES_IGNORE = None

CONFIG = conf.config_dict("test", {
  "pyflakes.ignore": [],
  "integ.test_directory": "./test/data",
})


def pep8_issues(base_path = DEFAULT_TARGET):
  """
  Checks for stylistic issues that are an issue according to the parts of PEP8
  we conform to.

  :param str base_path: directory to be iterated over

  :returns: dict of the form ``path => [(line_number, message)...]``
  """

  # The pep8 command give output of the form...
  #
  #   FILE:LINE:CHARACTER ISSUE
  #
  # ... for instance...
  #
  #   ./test/mocking.py:868:31: E225 missing whitespace around operator
  #
  # Ignoring the following compliance issues.
  #
  # * E251 no spaces around keyword / parameter equals
  #
  #   This one I dislike a great deal. It makes keyword arguments different
  #   from assignments which looks... aweful. I'm not sure what PEP8's author
  #   was on when he wrote this one but it's stupid.
  #
  #   Someone else can change this if they really care.
  #
  # * E501 line is over 79 characters
  #
  #   We're no longer on TTY terminals. Overly constraining line length makes
  #   things far less readable, encouraging bad practices like abbreviated
  #   variable names.
  #
  #   If the code fits on my tiny netbook screen then it's narrow enough.
  #
  # * E111 and E121 four space indentations
  #
  #   Ahhh, indentation. The holy war that'll never die. Sticking with two
  #   space indentations since it leads to shorter lines.
  #
  # * E127 continuation line over-indented for visual indent
  #
  #   Pep8 only works with this one if we have four space indents (its
  #   detection is based on multiples of four).

  ignored_issues = "E111,E121,E501,E251,E127"

  issues = {}
  pep8_output = system.call("pep8 --ignore %s %s" % (ignored_issues, base_path))

  for line in pep8_output:
    line_match = re.match("^(.*):(\d+):(\d+): (.*)$", line)

    if line_match:
      path, line, _, issue = line_match.groups()

      if not _is_test_data(path):
        issues.setdefault(path, []).append((int(line), issue))

  return issues


def pyflakes_issues(base_path = DEFAULT_TARGET):
  """
  Checks for issues via pyflakes. False positives can be whitelisted via our
  test configuration.

  :param str base_path: directory to be iterated over

  :returns: dict of the form ``path => [(line_number, message)...]``
  """

  global PYFLAKES_IGNORE

  if PYFLAKES_IGNORE is None:
    pyflakes_ignore = {}

    for line in CONFIG["pyflakes.ignore"]:
      path, issue = line.split("=>")
      pyflakes_ignore.setdefault(path.strip(), []).append(issue.strip())

    PYFLAKES_IGNORE = pyflakes_ignore

  # Pyflakes issues are of the form...
  #
  #   FILE:LINE: ISSUE
  #
  # ... for instance...
  #
  #   stem/prereq.py:73: 'long_to_bytes' imported but unused
  #   stem/control.py:957: undefined name 'entry'

  issues = {}
  pyflakes_output = system.call("pyflakes %s" % base_path)

  for line in pyflakes_output:
    line_match = re.match("^(.*):(\d+): (.*)$", line)

    if line_match:
      path, line, issue = line_match.groups()

      if not _is_test_data(path) and not issue in PYFLAKES_IGNORE.get(path, []):
        issues.setdefault(path, []).append((int(line), issue))

  return issues


def get_issues(base_path = DEFAULT_TARGET):
  """
  Checks python source code in the given directory for whitespace issues.

  :param str base_path: directory to be iterated over

  :returns: dict of the form ``path => [(line_number, message)...]``
  """

  # TODO: This does not check that block indentations are two spaces because
  # differentiating source from string blocks ("""foo""") is more of a pita
  # than I want to deal with right now.

  issues = {}

  for file_path in _get_files_with_suffix(base_path):
    if _is_test_data(file_path):
      continue

    with open(file_path) as f:
      file_contents = f.read()

    lines, file_issues, prev_indent = file_contents.split("\n"), [], 0
    is_block_comment = False

    for index, line in enumerate(lines):
      whitespace, content = re.match("^(\s*)(.*)$", line).groups()

      if '"""' in content:
        is_block_comment = not is_block_comment

      if "\t" in whitespace:
        file_issues.append((index + 1, "indentation has a tab"))
      elif "\r" in content:
        file_issues.append((index + 1, "contains a windows newline"))
      elif content != content.rstrip():
        file_issues.append((index + 1, "line has trailing whitespace"))

    if file_issues:
      issues[file_path] = file_issues

  return issues


def _is_test_data(path):
  return os.path.normpath(path).startswith(os.path.normpath(CONFIG["integ.test_directory"]))


def _get_files_with_suffix(base_path, suffix = ".py"):
  """
  Iterates over files in a given directory, providing filenames with a certain
  suffix.

  :param str base_path: directory to be iterated over
  :param str suffix: filename suffix to look for

  :returns: iterator that yields the absolute path for files with the given suffix
  """

  if os.path.isfile(base_path):
    if base_path.endswith(suffix):
      yield base_path
  else:
    for root, _, files in os.walk(base_path):
      for filename in files:
        if filename.endswith(suffix):
          yield os.path.join(root, filename)

if __name__ == '__main__':
  issues = get_issues()

  for file_path in issues:
    print file_path

    for line_number, msg in issues[file_path]:
      line_count = "%-4s" % line_number
      print "  line %s %s" % (line_count, msg)

    print
