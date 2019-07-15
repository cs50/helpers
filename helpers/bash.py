import re

from . import _common

from help50 import helper


@helper("bash")
def cd_no_such_file_or_directory(lines):
    """
      >>> "Are you sure" in cd_no_such_file_or_directory([  \
              "bash: cd: foo: No such file or directory"    \
          ])[1][0]
      True
    """
    matches = re.search(r"^{}: (?:line \d+: )?cd: (.+): No such file or directory".format(_common.BASH_PATH), lines[0])
    if not matches:
        return

    response = [
        "Are you sure `{}` exists?".format(matches.group(1)),
        "Did you misspell `{}`?".format(matches.group(1))
    ]

    return lines[0:1], response


@helper("bash")
def cd_not_a_directory(lines):
    """
      >>> "trying to change" in cd_not_a_directory([ \
              "bash: cd: foo: Not a directory"       \
          ])[1][0]
      True
    """
    matches = re.search(r"^{}: cd: (.+): Not a directory".format(_common.BASH_PATH), lines[0])
    if not matches:
        return

    response = [
        "Looks like you're trying to change directories, but `{}` isn't a directory.".format(matches.group(1)),
        "Did you mean to create the directory `{}` first?".format(matches.group(1))
    ]

    return lines[0:1], response


@helper("bash")
def command_not_found(lines):
    """
      >>> "Are you sure" in command_not_found([ \
              "bash: foo: command not found"    \
          ])[1][0]
      True
    """
    matches = re.search(r"^{}: (.+): command not found".format(_common.BASH_PATH), lines[0])
    if not matches:
        return

    if (matches.group(1) == "check"):
        response = ["Did you mean to execute `check50`?"]
    elif (matches.group(1) == "style"):
        response = ["Did you mean to execute `style50`?"]
    elif (matches.group(1) == "submit"):
        response = ["Did you mean to execute `submit50`?"]
    else:
        response = [
            "Are you sure `{}` exists?".format(matches.group(1)),
            "Did you misspell `{}`?".format(matches.group(1)),
            "Did you mean to execute `./{}`?".format(matches.group(1))
        ]

    return lines[0:1], response


@helper("bash")
def dot_slash_no_such_file_or_directory(lines):
    """
      >>> "Are you sure" in dot_slash_no_such_file_or_directory([ \
              "bash: ./foo: No such file or directory"            \
          ])[1][0]
      True
    """
    matches = re.search(r"^{}: ./(.+): No such file or directory".format(_common.BASH_PATH), lines[0])
    if not matches:
        return

    response = [
        "Are you sure `{}` exists?".format(matches.group(1)),
        "Did you misspell `{}`?".format(matches.group(1)),
        "Did you mean to execute `{}` instead of `./{}`?".format(matches.group(1), matches.group(1))
    ]

    return lines[0:1], response


@helper("bash")
def permission_denied(lines):
    """
      >>> "couldn't be executed" in permission_denied([ \
              "bash: ./foo: Permission denied"          \
          ])[1][0]
      True
    """
    matches = re.search(r"^{}: .*?(([^/]+?)\.?([^/.]*)): Permission denied".format(_common.BASH_PATH), lines[0])
    if not matches:
        return

    response = [
        "`{}` couldn't be executed.".format(matches.group(1))
    ]

    if (matches.group(3).lower() == "c"):
        response.append("Did you mean to execute `./{}`?".format(matches.group(2)))
    elif (matches.group(3).lower() == "pl"):
        response.append("Did you mean to execute `perl {}`?".format(matches.group(1)))
    elif (matches.group(3).lower() == "php"):
        response.append("Did you mean to execute `php {}`?".format(matches.group(1)))
    elif (matches.group(3).lower() == "rb"):
        response.append("Did you mean to execute `ruby {}`?".format(matches.group(1)))
    else:
        response.append("Does `{}` definitely exist?".format(matches.group(1)))
        response.append("Do you need to make `{}` executable with " \
            "`chmod +x {}`?".format(matches.group(1), matches.group(1)))

    return lines[0:1], response
