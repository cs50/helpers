import re

import regex

from help50 import helper


@helper("rm")
def remove_regular_file(lines):
    """
      >>> "will delete the" in remove_regular_file([ \
              "rm: remove regular file ‘foo’?"       \
          ])[1][0]
      True

      >>> "empty anyway" in remove_regular_file([    \
              "rm: remove regular empty file ‘foo’?" \
          ])[1][0]
      True
    """
    matches = re.search(r"^{}rm: remove regular (?:empty )?file ‘(.+)’\?".format(regex.FILE_PATH), lines[0])
    if not matches:
        return

    empty = re.search(r"^.*rm: remove regular empty file", lines[0])

    response = [
        "The command you typed will delete the file `{}`".format(matches.group(1))
    ]

    response[0] += " (which is empty anyway)." if empty else "."
    response.append("If you wish to delete `{}`, type `y` and press return.".format(matches.group(1)))
    response.append("Typing `n` and pressing return will cancel the operation.")

    return lines[0:1], response
