# Copyright (c) 2010 by Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# This file is part of hghooks.
#
# hghooks is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# hghooks is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with hghooks.  If not, see <http://www.gnu.org/licenses/>.

import compiler
import os
import re
import sys
import _ast

try:
    import pep8
    HAS_PEP8 = True
except ImportError:
    HAS_PEP8 = False

try:
    import pyflakes.checker
    HAS_PYFLAKES = True
except ImportError:
    HAS_PYFLAKES = False

try:
    import pyjslint
    HAS_JSLINT = True
except ImportError:
    HAS_JSLINT = False

from hghooks import CheckerManager, re_options


def pep8_checker(pep8_options):
    extra_args = []
    for key, value in pep8_options.iteritems():
        value_spec = ','.join([ign.strip(', ') for ign in value.split()
                              if ign.strip(', ')])
        extra_args.append('--%s=%s' % (key, value_spec))

    def check_pep8(files_to_check, msg):
        for filename, data in files_to_check.items():
            parentdir = os.path.dirname(filename)
            if not os.path.exists(parentdir):
                os.makedirs(parentdir)
            open(filename, 'w').write(data)

        # monkey patch sys.argv options so we can call pep8
        old_args = sys.argv
        sys.argv = ['pep8'] + files_to_check.keys() + extra_args
        options, args = pep8.process_options()
        sys.argv = old_args
        for path in args:
            pep8.input_file(path)

        return pep8.get_count()

    return check_pep8


def pep8hook(ui, repo, hooktype, node, pending, **kwargs):
    if not HAS_PEP8:
        ui.warn('You need the pep8 python module to use the pep8hook')
        return True  # Failure

    pep8_options = {}
    options = ['exclude', 'filename', 'select', 'ignore', 'max-line-length']
    for opt in options:
        if ui.config('pep8', opt, ''):
            pep8_options[opt] = ui.config('pep8', opt, '')
            
    checker_manager = CheckerManager(ui, repo, node, 'no-pep8')
    return checker_manager.check(pep8_checker(pep8_options))


pdb_catcher = re.compile(r'^[^#]*pdb\.set_trace\(\)', re_options)


def pdb_checker(files_to_check, msg):

    def check_one_file(data, filename):
        warnings = len(pdb_catcher.findall(data))
        if warnings > 0:
            print '%s: pdb found' % filename
        return warnings

    return sum([check_one_file(data, filename)
                for filename, data in files_to_check.items()])


def pdbhook(ui, repo, hooktype, node, pending, **kwargs):
    checker_manager = CheckerManager(ui, repo, node, 'no-pdb')
    return checker_manager.check(pdb_checker)


def pyflakes_version():
    return tuple([int(part) for part in pyflakes.__version__.split('.')])


def pyflakes_check(data, filename):
    """
    Check the Python source given by C{data} for flakes.

    It's like pyflakes.scripts.check function but ignores those lines which
    ends with ends with a "pyflakes:ignore" comment.

    Code adapted from pyflakes.scripts.pyflakes.check function.
    """
    # First, compile into an AST and handle syntax errors.
    try:
        tree = compile(data, filename, "exec", _ast.PyCF_ONLY_AST)
    except SyntaxError, value:
        msg = value.args[0]

        (lineno, offset, text) = value.lineno, value.offset, value.text

        # If there's an encoding problem with the file, the text is None.
        if text is None:
            # Avoid using msg, since for the only known case, it contains a
            # bogus message that claims the encoding the file declared was
            # unknown.
            print >> sys.stderr, "%s: problem decoding source" % (filename, )
        else:
            line = text.splitlines()[-1]

            if offset is not None:
                offset = offset - (len(text) - len(line))

            print >> sys.stderr, '%s:%d: %s' % (filename, lineno, msg)
            print >> sys.stderr, line

            if offset is not None:
                print >> sys.stderr, " " * offset, "^"

        return 1
    else:
        if pyflakes_version() < (0, 5, 0):
            tree = compiler.parse(data)

        # Okay, it's syntactically valid.  Now check it.
        w = pyflakes.checker.Checker(tree, filename)

        lines = data.split('\n')
        # Ignoring lines with a "pyflakes:ignore" comment at the end
        messages = [message for message in w.messages
                    if lines[message.lineno - 1].find('pyflakes:ignore') < 0]
        messages.sort(lambda a, b: cmp(a.lineno, b.lineno))
        for warning in messages:
            print warning
        return len(messages)


def pyflakes_checker(files_to_check, msg):
    return sum([pyflakes_check(data, filename)
                for filename, data in files_to_check.items()])


def pyflakeshook(ui, repo, hooktype, node, pending, **kwargs):
    if not HAS_PYFLAKES:
        ui.warn('You need the pyflakes python module to use the pyflakeshook')
        return True  # Failure

    checker_manager = CheckerManager(ui, repo, node, 'no-pyflakes')
    return checker_manager.check(pyflakes_checker)


def jslint_check(data, filename):
    output = pyjslint.check_JSLint(data)
    if len(output) > 0:
        print >> sys.stderr, "%s: problem decoding source" % (filename, )
        print >> sys.stderr, '\n'.join(output)
        return 1
    return 0


def jslint_checker(files_to_check, msg):
    return sum([jslint_check(data, filename)
                for filename, data in files_to_check.items()])


def jslinthook(ui, repo, hooktype, node, pending, **kwargs):
    if not HAS_JSLINT:
        ui.warn('You need the pyjslint python module to use the jslinthook')
        return True  # Failure

    checker_manager = CheckerManager(ui, repo, node, 'no-jslint',
                                     extension='.js')
    return checker_manager.check(jslint_checker)
