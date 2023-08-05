"""Removes unused imports as reported by pyflakes."""

from __future__ import print_function

import io
import os
import tokenize


__version__ = '0.1.6'


PYFLAKES_BIN = 'pyflakes'


try:
    unicode
except NameError:
    unicode = str


class MissingExecutableException(Exception):

    """Raised when executable is missing."""


def standard_package_names():
    """Yield list of standard module names."""
    from distutils import sysconfig
    path = sysconfig.get_python_lib(standard_lib=True)

    for name in (
            frozenset(os.listdir(path)) |
            frozenset(os.listdir(os.path.join(path, 'lib-dynload')))):

        if name.startswith('_') or '-' in name:
            continue

        if '.' in name and name.rsplit('.')[-1] not in ['so', 'py', 'pyc']:
            continue

        yield name.split('.')[0]


IMPORTS_WITH_SIDE_EFFECTS = {'antigravity', 'rlcompleter', 'this'}

# In case they are built into CPython.
BINARY_IMPORTS = {'datetime', 'grp', 'io', 'json', 'math', 'multiprocessing',
                  'parser', 'pwd', 'string', 'os', 'sys', 'time'}

SAFE_IMPORTS = (frozenset(standard_package_names()) -
                IMPORTS_WITH_SIDE_EFFECTS |
                BINARY_IMPORTS)


def unused_import_line_numbers(source):
    """Yield line numbers of unused imports."""
    import tempfile
    (_temp_open_file, temp_filename) = tempfile.mkstemp()
    os.close(_temp_open_file)

    with open_with_encoding(temp_filename, encoding='utf-8', mode='w') as f:
        f.write(source)

    for line in run_pyflakes(temp_filename):
        if line.rstrip().endswith('imported but unused'):
            yield int(line.split(':')[1])

    os.remove(temp_filename)


def run_pyflakes(filename):
    """Yield output of pyflakes."""
    assert ':' not in filename

    import subprocess
    try:
        process = subprocess.Popen(
            [PYFLAKES_BIN, filename],
            stdout=subprocess.PIPE)

        while process.poll() is None:
            line = process.stdout.readline().decode('utf-8').strip()
            if ':' in line:
                yield line

        for line in process.communicate()[0].decode('utf-8').splitlines():
            if ':' in line:
                yield line

    except OSError:
        raise MissingExecutableException()


def extract_package_name(line):
    """Return package name in import statement."""
    assert '\\' not in line
    assert '(' not in line
    assert ')' not in line
    assert ';' not in line

    if line.lstrip().startswith('import'):
        word = line.split()[1]
    elif line.lstrip().startswith('from'):
        word = line.split()[1]
    else:
        # Ignore doctests.
        return None

    package = word.split('.')[0]
    assert ' ' not in package

    return package


def multiline_import(line):
    """Return True if import is spans multiples lines."""
    for symbol in '\\();':
        if symbol in line:
            return True
    return False


def break_up_import(line):
    """Return line with imports on separate lines."""
    assert '\\' not in line
    assert '(' not in line
    assert ')' not in line
    assert ';' not in line

    newline = get_line_ending(line)

    import re
    (indentation, imports) = re.split(pattern=r'\bimport\b',
                                      string=line, maxsplit=1)

    if '#' in imports:
        (imports, comment) = imports.split('#', maxsplit=1)
        comment = '  # ' + comment.strip()
    else:
        comment = ''

    indentation += 'import '
    assert newline

    return ''.join([indentation + i.strip() + comment + newline
                    for i in imports.split(',')])


def filter_code(source, additional_imports=None):
    """Yield code with unused imports removed."""
    imports = SAFE_IMPORTS
    if additional_imports:
        imports |= frozenset(additional_imports)
    del additional_imports

    marked_lines = frozenset(unused_import_line_numbers(source))
    sio = io.StringIO(source)
    for line_number, line in enumerate(sio.readlines(), start=1):
        if (line_number in marked_lines and not multiline_import(line)):
            if ',' in line:
                yield break_up_import(line)
                continue

            package = extract_package_name(line)
            if package not in imports:
                yield line
            elif line.lstrip() != line:
                # Remove indented unused import.
                yield get_indentation(line) + 'pass' + get_line_ending(line)
            else:
                # Discard unused import line.
                pass
        else:
            yield line


def useless_pass_line_numbers(source):
    """Yield line numbers of unneeded "pass" statements."""
    sio = io.StringIO(source)
    previous_token_type = None
    for token in tokenize.generate_tokens(sio.readline):
        token_type = token[0]
        start_row = token[2][0]
        line = token[4]

        is_pass = (token_type == tokenize.NAME and line.strip() == 'pass')

        # TODO: Leading "pass".

        # Trailing "pass".
        if is_pass and previous_token_type != tokenize.INDENT:
            yield start_row

        previous_token_type = token_type


def filter_useless_pass(source):
    """Yield code with useless "pass" lines removed."""
    try:
        marked_lines = frozenset(useless_pass_line_numbers(source))
    except (tokenize.TokenError, IndentationError):
        marked_lines = frozenset()

    sio = io.StringIO(source)
    for line_number, line in enumerate(sio.readlines(), start=1):
        if line_number not in marked_lines:
            yield line


def get_indentation(line):
    """Return leading whitespace."""
    if line.strip():
        non_whitespace_index = len(line) - len(line.lstrip())
        return line[:non_whitespace_index]
    else:
        return unicode()


def get_line_ending(line):
    """Return line ending."""
    non_whitespace_index = len(line.rstrip()) - len(line)
    return line[non_whitespace_index:]


def fix_code(source, additional_imports=None):
    """Return code with all filtering run on it."""
    filtered_source = None
    while True:
        filtered_source = unicode().join(
            filter_useless_pass(unicode().join(
                filter_code(source,
                            additional_imports=additional_imports))))
        if filtered_source == source:
            break
        source = filtered_source

    return filtered_source


def fix_file(filename, args, standard_out):
    """Run fix_code() on file."""
    encoding = detect_encoding(filename)
    with open_with_encoding(filename, encoding=encoding) as input_file:
        source = input_file.read()

    original_source = source
    filtered_source = fix_code(
        source,
        additional_imports=args.imports.split(',') if args.imports else None)

    if original_source != filtered_source:
        if args.in_place:
            with open_with_encoding(filename, mode='w',
                                    encoding=encoding) as output_file:
                output_file.write(filtered_source)
        else:
            import difflib
            diff = difflib.unified_diff(
                io.StringIO(original_source).readlines(),
                io.StringIO(filtered_source).readlines(),
                'before/' + filename,
                'after/' + filename)
            standard_out.write(unicode().join(diff))


def open_with_encoding(filename, encoding, mode='r'):
    """Return opened file with a specific encoding."""
    return io.open(filename, mode=mode, encoding=encoding,
                   newline='')  # Preserve line endings


def detect_encoding(filename):
    """Return file encoding."""
    try:
        with open(filename, 'rb') as input_file:
            from lib2to3.pgen2 import tokenize as lib2to3_tokenize
            encoding = lib2to3_tokenize.detect_encoding(input_file.readline)[0]

            # Check for correctness of encoding.
            with open_with_encoding(filename, encoding) as input_file:
                input_file.read()

        return encoding
    except (SyntaxError, LookupError, UnicodeDecodeError):
        return 'latin-1'


def main(argv, standard_out, standard_error):
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description=__doc__, prog='autoflake')
    parser.add_argument('-i', '--in-place', action='store_true',
                        help='make changes to files instead of printing diffs')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='drill down directories recursively')
    parser.add_argument('--imports',
                        help='by default, only unused standard library '
                             'imports are removed; specify a comma-separated '
                             'list of additional modules/packages')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('files', nargs='+', help='files to format')

    args = parser.parse_args(argv[1:])

    filenames = list(set(args.files))
    while filenames:
        name = filenames.pop(0)
        if args.recursive and os.path.isdir(name):
            for root, directories, children in os.walk(name):
                filenames += [os.path.join(root, f) for f in children
                              if f.endswith('.py') and
                              not f.startswith('.')]
                for d in directories:
                    if d.startswith('.'):
                        directories.remove(d)
        else:
            try:
                fix_file(name, args=args, standard_out=standard_out)
            except IOError as exception:
                print(exception, file=standard_error)
