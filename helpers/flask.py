import re

from . import _common

from help50 import helper


@helper("flask")
def did_not_provide_env_var(lines):
    """
      >>> "assumes is set" in did_not_provide_env_var([                                                            \
              "Usage: flask run [OPTIONS]",                                                                        \
              "",                                                                                                  \
              "Error: Could not locate Flask application. You did not provide the FLASK_APP environment variable." \
          ])[1][0]
      True
    """
    matches = re.search(r"Usage: flask run \[OPTIONS\]", lines[0])
    if not matches:
        return

    if len(lines) >= 3:
        matches = re.search(r"You did not provide the FLASK_APP environment variable", lines[2])
        if matches:
            response = [
                "Looks like `FLASK_APP`, which `flask` assumes is set, isn't set.",
                "If your application is in `application.py`, try running `FLASK_APP=application.py flask run`."
            ]

            return lines[0:3], response


@helper("flask")
def file_path_does_not_exist(lines):
    """
      >>> "wrong directory" in file_path_does_not_exist([                                                           \
              "Usage: flask run [OPTIONS]",                                                                         \
              "",                                                                                                   \
              "Error: The file/path provided (application.py) does not appear to exist. Please verify the path is " \
                  "correct. If app is not on PYTHONPATH, ensure the extension is .py"                               \
          ])[1][0]
      True
    """
    matches = re.search(r"Usage: flask run \[OPTIONS\]", lines[0])
    if not matches:
        return

    if len(lines) >= 3:
        matches = re.search(r"Error: The file/path provided \((.+)\) does not appear to exist", lines[2])
        if matches:
            response = [
                "Looks like you might have run `flask` in the wrong directory.",
                "Are you sure `{}` exists in your current directory?".format(matches.group(1))
            ]

            return lines[0:3], response
