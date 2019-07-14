import re

import regex

from help50 import helper


@helper("cp")
def overwrite(lines):
    """
      >>> "You are copying" in overwrite([ \
              "cp: overwrite ‘bar’?"       \
          ])[1][0]
      True

      >>> "You are copying" in overwrite([ \
              "cp: overwrite ‘baz/bar’?"   \
          ])[1][0]
      True
    """
    matches = re.search(r"^{}cp: overwrite ‘(.+)’\?".format(regex.FILE_PATH), lines[0])
    if not matches:
        return

    # if "/" is present in destination path, then assume copying to a new directory
    new_dir = "/" in matches.group(1)
    interpretation = "You are copying a file to `{}`, but there is already a file ".format(matches.group(1))
    interpretation += "there " if new_dir else "in the current directory "
    interpretation += "with the same name."

    response = [interpretation]
    response.append("To copy the file, replacing the old version, type `y` and press return.")
    response.append("Typing `n` and pressing return will cancel copying.")

    return lines[0:1], response
