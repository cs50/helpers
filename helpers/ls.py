import re

from . import _common

from help50 import helper


@helper("ls")
def cannot_access(lines):
    """
      >>> "Are you sure" in cannot_access([                       \
              "ls: cannot access asdf: No such file or directory" \
          ])[1][0]
      True
    """
    matches = re.search(r"^{}ls: cannot access (.+): No such file or directory".format(_common.FILE_PATH), lines[0])
    if not matches:
        return

    response = [
        "Are you sure `{}` exists?".format(matches.group(1)),
        "Did you misspell `{}`?".format(matches.group(1))
    ]

    return lines[0:1], response
