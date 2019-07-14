import re

import regex

from help50 import helper


@helper("mv")
def overwrite(lines):
    """
      >>> "You are" in overwrite([   \
              "mv: overwrite ‘bar’?" \
          ])[1][0]
      True

      >>> "You are" in overwrite([       \
              "mv: overwrite ‘baz/foo’?" \
          ])[1][0]
      True
    """
    matches = re.search(r"^{}mv: overwrite ‘(.+)’\?".format(regex.FILE_PATH), lines[0])
    if not matches:
        return

    # if a "/" is present in the destination path, assume moving a file; otherwise, renaming a file
    moving = "/" in matches.group(1)

    interpretation = "You are "
    interpretation += "moving " if moving else "renaming "
    interpretation += "a file to `{}`, but there is already a file with the same name ".format(matches.group(1))
    interpretation += "there." if moving else "in the current directory."

    response = [interpretation]
    response.append("To replace the old file, type `y` and press return.")
    response.append("Typing `n` and pressing return will cancel the operation.")

    return lines[0:1], response
