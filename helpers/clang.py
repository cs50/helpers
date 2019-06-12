import collections
import re

from help50 import helper


@helper("clang")
def invalid_append_string(lines):
    """
    >>> output = "test.c:6:15: error: adding 'char' to a string does not append to the string [-Werror, -Wstring-plus-int]\\n    printf(\"\" + c);"
    >>> invalid_append_string(output.splitlines())[1][0]
    "Careful, you can't concatenate values and strings in C using the `+` operator, as you seem to be trying to do on line 6 of `test.c`."
    """
    matches = _match(r"adding '(.+)' to a string does not append to the string", lines[0])
    if not matches:
        return

    response = ["Careful, you can't concatenate values and strings in C using the `+` operator, " \
                "as you seem to be trying to do on line {} of `{}`.".format(matches.line, matches.file)]

    if len(lines) >= 2 and re.search(r"printf\s*\(", lines[1]):
        response.append("Odds are you want to provide `printf` with a format code for that value and pass that value to `printf` as an argument.")
        return lines, response
    return lines[0:1], response



@helper("clang")
def array_bounds(lines):
    """
    >>> output = 'test.c:5:20: error: array index 1 is past the end of the array (which contains 1 element) [-Werror,-Warray-bounds]\\n    printf("%d\\\\n", a[1]);\\n                   ^ ~'
    >>> array_bounds(output.splitlines())[1][0]
    "Careful, on line 5 of `test.c`, it looks like you're trying to access location 1 of `a`, which doesn't exist; `a` isn't that long."
    """
    matches = _match(r"array index (\d+) is past the end of the array", lines[0])
    if not matches:
        return

    array = _caret_extract(lines[1:3])
    if array:
        response = ["Careful, on line {} of `{}`, it looks like you're trying to access location {} of `{}`, which doesn't exist; `{}` isn't that long.".format(matches.line, matches.file, matches.group[0], array, array)]
    else:
        response = ["Careful, on line {} of `{}`, it looks like you're trying to access location {} of an array, which doesn't exist; the array isn't that long.".format(matches.line, matches.file, matches.group[0])]
    response.append("Keep in mind that arrays are 0-indexed.")

    if array:
        return lines[0:3], response
    return lines[0:1], response



@helper("clang")
def bad_define(lines):
    """
    >>> output = "foo.c:18:1: error: unknown type name 'define'\\ndefine _XOPEN_SOURCE 500\\n^"
    >>> bad_define(output.splitlines())[1][0]
    'If trying to define a constant on line 18 of `foo.c`, be sure to use `#define` rather than just `define`.'
    """

    matches = _match(r"unknown type name 'define'", lines[0])
    if matches:
        response = [
            "If trying to define a constant on line {} of `{}`, be sure to use `#define` rather than just `define`.".format(matches.line, matches.file)
        ]
        return lines[0:3 if len(lines) >= 3 else 1], response


@helper("clang")
def bad_include(lines):
    """
    >>> output = "foo.c:18:1: error: unknown type name 'include'\\ninclude <stdio.h>\\n^"
    >>> bad_include(output.splitlines())[1][0]
    'If trying to include a header file on line 18 of `foo.c`, be sure to use `#include` rather than just `include`.'
    """
    matches = _match("unknown type name 'include'", lines[0])
    if matches:
        response = [
            "If trying to include a header file on line {} of `{}`, be sure to use `#include` rather than just `include`.".format(matches.line, matches.file)
        ]
        return lines[0:3 if len(lines) >= 3 else 1], response


@helper("clang")
def unknown_type(lines):
    """
    >>> output = "foo.c:1:1: error: unknown type name 'bar'\\nbar baz\\n^"
    >>> unknown_type(output.splitlines())[1][0]
    "You seem to be using `bar` on line 1 of `foo.c` as though it's a type, even though it's not been defined as one."
    """
    matches = _match(r"unknown type name '(.+)'", lines[0])

    if not matches:
        return

    response = [
        "You seem to be using `{}` on line {} of `{}` as though it's a type, even though it's not been defined as one.".format(matches.group[0], matches.line, matches.file)
    ]

    if matches.group[0] == "bool":
        response.append("Did you forget `#include <cs50.h>` or `#include <stdbool.h>` atop `{}`?".format(matches.file))
    elif matches.group[0] == "size_t":
        response.append("Did you forget `#include <string.h>` atop `{}`?".format(matches.file))
    elif matches.group[0] == "string":
        response.append("Did you forget `#include <cs50.h>` atop `{}`?".format(matches.file))
    else:
        response.append("Did you perhaps misspell `{}` or forget to `typedef` it?".format(matches.group[0]))

    return lines[0:3 if len(lines) >= 3 else 1], response


@helper("clang")
def unused_var(lines):
    """
    >>> output = "foo.c:6:9: error: unused variable 'x' [-Werror,-Wunused-variable]\\n    int x = 28;\\n        ^"
    >>> unused_var(output.splitlines())[1][0]
    'It seems that the variable `x` (declared on line 6 of `foo.c`) is never used in your program. Try either removing it altogether or using it.'
    """
    matches = _match(r"unused variable '([^']+)'", lines[0])
    if not matches:
        return

    response = [
        "It seems that the variable `{}` (declared on line {} of `{}`) is never used in your program. Try either removing it altogether or using it.".format(matches.group[0], matches.line, matches.file)
    ]
    return lines[0:1], response


@helper("clang")
def self_initialization(lines):
    """
    >>> output = "water.c:8:15: error: variable 'x' is uninitialized when used within its own initialization [-Werror,-Wuninitialized]\\nint x= 12*x;\\n     ~     ^"
    >>> self_initialization(output.splitlines())[1][0]
    "Looks like you have `x` on both the left- and right-hand side of the `=` on line 8 of `water.c`, but `x` doesn't yet have a value."
    """
    matches = _match(r"variable '(.+)' is uninitialized when used within its own initialization", lines[0])
    if not matches:
        return
    response = [
        "Looks like you have `{}` on both the left- and right-hand side of the `=` on line {} of `{}`, but `{}` doesn't yet have a value.".format(matches.group[0], matches.line, matches.file, matches.group[0]),
        "Be sure not to initialize `{}` with itself.".format(matches.group[0])
    ]
    if len(lines) >= 3 and re.search(r"^\s*~\s*\^\s*$", lines[2]):
        return lines[0:3], response
    return lines[0:1], response


@helper("clang")
def void_return(lines):
    """
    >>> output = "foo.c:6:10: error: void function 'f' should not return a value [-Wreturn-type]\\n    return 0;\\n    ^      ~"
    >>> void_return(output.splitlines())[1][0]
    'It looks like your function, `f`, is returning `0` on line 6 of `foo.c`, but its return type is `void`.'
    """
    matches = _match(r"void function '(.+)' should not return a value", lines[0])
    if matches:
        value = _tilde_extract(lines[1:3])
        if len(lines) >= 3 and value:
            response = [
                "It looks like your function, `{}`, is returning `{}` on line {} of `{}`, but its return type is `void`.".format(matches.group[0], value, matches.line, matches.file),
                "Are you sure you want to return a value?"
            ]
            return lines[0:3], response
        else:
            response = [
                "It looks like your function, `{}`, is returning a value on line {} of `{}`, but its return type is `void`.".format(matches.group[0], matches.line, matches.file),
                "Are you sure you want to return a value?"
            ]
            return lines[0:1], response

@helper("clang")
def array_subscript(lines):
    """
    >>> output = "foo.c:6:21: error: array subscript is not an integer\\n" \
                 "    printf(\\"%i\\\\n\\", x[\\"28\\"]);\\n" \
                 "                    ^~~~~"
    >>> array_subscript(output.splitlines())[1][0]
    'Looks like you\\'re trying to access an element of the array `x` on line 6 of `foo.c`, but your index (`"28"`) is not of type `int`.'
    """
    matches = _match(r"array subscript is not an integer", lines[0])

    if not matches:
        return

    array = _caret_extract(lines[1:3], left_aligned=False)
    index = _tilde_extract(lines[1:3])
    if array and index:
        response = [
            "Looks like you're trying to access an element of the array `{}` on line {} of `{}`, but your index (`{}`) is not of type `int`.".format(array, matches.line, matches.file, index)
        ]
        if index[0] == index[-1] == '"':
            response.append("Right now, your index is of type `string` instead.")
    else:
        response = [
            "Looks like you're trying to access an element of an array on line {} of `{}`, but your index is not of type `int`.".format(matches.line, matches.file)
        ]
    response.append("Make sure your index (the value between square brackets) is an `int`.")
    if len(lines) >= 2 and re.search(r"[.*]", lines[1]):
        return lines[0:2], response
    return lines[0:1], response



@helper("clang")
def missing_parens(lines):
    """
    >>> output = "foo.c:1:3: error: assigning to 'float' from incompatible type 'float (void)'\\n" \
            "        f = get_float\\n" \
            "          ^ ~~~~~~~~~\\n"
    >>> missing_parens(output.splitlines())[1][0]
    "Looks like you're trying to call `get_float` on line 1 of `foo.c`, but did you forget parentheses after the function's name?"
    """
    matches = _match(r"assigning to '(.+)' from incompatible type '.+ \(.+\)'", lines[0])
    if not matches:
        return

    function = _tilde_extract(lines[1:3])
    if function:
        response = [
            "Looks like you're trying to call `{}` on line {} of `{}`, but did you forget parentheses after the function's name?".format(function, matches.line, matches.file)
        ]
        return lines[0:3], response;
    else:
        response = [
            "Looks like you're trying to call a function on line {} of `{}`, but did you forget parentheses after the function's name?".format(matches.line, matches.file)
        ]
        return lines[0:1], response;


@helper("clang")
def conflicting_types(lines):
    """
    >>> output = "foo.c:3:12: error: conflicting types for 'round'\\n" \
                 "int round(int n);\\n" \
                 "    ^"
    >>> conflicting_types(output.splitlines())[1][0]
    "Looks like you're redeclaring the function `round`, but with a different return type on line 3 of `foo.c`."
    """

    matches = _match(r"conflicting types for '(.*)'", lines[0])
    if not matches:
        return

    response = [
        "Looks like you're redeclaring the function `{}`, but with a different return type on line {} of `{}`.".format(matches.group[0], matches.line, matches.file)
    ]
    if len(lines) >= 4:
        prev_declaration = re.search(r"^([^:]+):(\d+):\d+: note: previous declaration is here", lines[3])
        if prev_declaration:
            if matches.file == prev_declaration.group(1):
                response.append("You had already declared this function on line {}.".format(prev_declaration.group(2)))
            else:
                response.append("The function `{}` is already declared in the library {}. Try renaming your function.".format(matches.group[0], prev_declaration.group(1).split('/')[-1]))
            return lines[0:4], response
    return lines[0:1], response


@helper("clang")
def continue_not_in_loop(lines):
    """
    >>> output = "test.c:51:17: error: 'continue' statement not in loop statement\\n" \
                 "                 continue;\\n" \
                 "                 ^"
    >>> continue_not_in_loop(output.splitlines())[1][0]
    "Looks like you're trying to use `continue` on line 51 of `test.c`, which isn't inside of a loop, but that keyword can only be used inside of a loop."
    """
    matches = _match(r"'continue' statement not in loop statement", lines[0])
    if not matches:
        return

    response = [
        "Looks like you're trying to use `continue` on line {} of `{}`, which isn't inside of a loop, but that keyword can only be used inside of a loop.".format(matches.line, matches.file)
    ]
    return lines[0:1], response


def control_reaches_non_void(lines):
    """
    >>> output = "foo.c:3:16: warning: control reaches end of non-void function [-Wreturn-type]\\n" \
                 "int foo(void) {}\\n" \
                 "               ^"

    >>> control_reaches_non_void(output.splitlines())[1][0]
    'Ensure that your function will always return a value. If your function is not meant to return a value, try changing its return type to `void`.'
    """
    matches = _match(r"control (may )?reach(es)? end of non-void function", lines[0])
    if not matches:
        return
    response = ["Ensure that your function will always return a value. If your function is not meant to return a value, try changing its return type to `void`."]
    return lines[0:1], response


@helper("clang")
def unused_arg_in_fmt_string(lines):
    """
    >>> bool(unused_arg_in_fmt_string([                                                                  \
            'foo.c:5:29: error: data argument not used by format string [-Werror,-Wformat-extra-args]',  \
            '    printf("%d %d", 27, 28, 29);',                                                          \
            '           ~~~~~~~          ^'                                                              \
        ]))
    True
    """

    matches = _match(r"data argument not used by format string", lines[0])

    if not matches:
        return

    response = [
        "You have more arguments in your formatted string on line {} of `{}` than you have format codes.".format(matches.line, matches.file),
        "Make sure that the number of format codes equals the number of additional arguments.",
        "Try either adding format code(s) or removing argument(s)."
    ]

    if len(lines) >= 2 and re.search(r"%", lines[1]):
        return lines[0:2], response
    return lines[0:1], response


#TODO: Copy the rest from help50-server

# HELPERS FOR THE HELPERS

def _caret_extract(lines, left_aligned=True):
    """
    Extract the name of a variable above the ^ by default, assumes that ^ is
    under the first character of the variable.
    If left_aligned is set to False, ^ is under the next character after the variable
    """
    if len(lines) < 2 or not _has_caret(lines[1]):
        return
    index = lines[1].index("^")

    if left_aligned:
        matches = re.match(r"^([A-Za-z0-9_]+)", lines[0][index:])
    else:
        matches = re.match(r"^.*?([A-Za-z0-9_]+)$", lines[0][:index])
    return matches.group(1) if matches else None

def _has_caret(line):
    """Returns true if line contains a caret diagnostic."""
    return bool(re.search(r"^[ ~]*\^[ ~]*$", line))


_ClangMatch = collections.namedtuple("_ClangMatch", ["file", "line", "group"])


def _match(expression, line, raw=False):
    """
    Performs a regular-expression match on a particular clang error or warning message.
    The first capture group is the filename associated with the message.
    The second capture group is the line number associated with the message.
    set raw=True to search for a message that doesn't follow clang's typical error output format.
    """
    query = expression if raw else fr"^([^:\s]+):(\d+):\d+: (?:warning|(?:fatal |runtime )?error): {expression}"
    matches = re.search(query, line)
    if not matches:
        return None
    if raw:
        return _ClangMatch(file=None, line=None, group=matches.groups())
    else:
        return _ClangMatch(file=matches.group(1),
                           line=matches.group(2),
                           group=matches.groups()[2:])


def _tilde_extract(lines):
    """Extracts all characters above the first sequence of ~."""
    if len(lines) < 2 or not re.search("~", lines[1]):
        return

    start = lines[1].index("~")
    length = 1

    while len(lines[1]) > start + length and lines[1][start + length] == "~":
        length += 1

    if len(lines[0]) >= start + length:
        return lines[0][start:start+length]
