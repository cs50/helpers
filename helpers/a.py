import re

from help50 import helper


@helper("a")
def floating_point_exception(lines):
    """
      >>> "trying to divide a number by 0" in floating_point_exception([ \
              "Floating point exception"                                 \
          ])[1][0]
      True
    """
    matches = re.match("Floating point exception", lines[0])
    if not matches:
        return

    response = [
        "Looks like somewhere in your program, you're trying to divide a number by 0.",
        "Check to see where in your program you're using the `/` or `%` operators, and be sure you never divide by 0 or " \
            "calculate a number modulo 0.",
        "If still unsure of where the problem is, stepping through your code with `debug50` may be helpful!"
    ]

    return lines[0:1], response


@helper("a")
def segmentation_fault(lines):
    """
      >>> "isn't supposed to access" in segmentation_fault([ \
              "Segmentation fault"                           \
          ])[1][0]
      True
    """
    matches = re.match("Segmentation fault", lines[0])
    if not matches:
        return

    response = [
        "Looks like your program is trying to access areas of memory that it isn't supposed to access.",
        "Did you try to change a character in a hardcoded string?",
        "Are you accessing an element of an array beyond the size of the array?",
        "Are you dereferencing a pointer that you haven't initialized?",
        "Are you dereferencing a pointer whose value is `NULL`?",
        "Are you dereferencing a pointer after you've freed it?"
    ]

    return lines[0:1], response


# TODO fix doctest
# @helper("a")
# def segmentation_fault_bool(lines):
#     """
#       >>> "store a value other than" in segmentation_fault_bool([ \
#               "Segmentation fault"                                \
#           ])[1][0]
#       True
#     """
#     matches = re.match("^(.+):(\d+):\d+: runtime error: load of value \d+, which is not a valid value for " \
#         "type '_Bool'$", lines[0])
#     if not matches:
#         return
# 
#     response = [
#         "Looks like, on line {} of `{}`, you're trying to store a value other than `true` or `false` in " \
#             "a `bool`?".format(matches.group(2), matches.group(1))
#     ]
# 
#     return lines[0:1], response
