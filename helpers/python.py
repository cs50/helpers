import re

from help50 import helper


@helper("python")
def catch_all_python(lines):
    """
      >>> "environment variable" in catch_all_python([                       \
              "Traceback (most recent call last):",                          \
              " File \\"./tweets\\", line 45, in <module>",                  \
              "   main()",                                                   \
              " File \\"./tweets\\", line 19, in main",                      \
              "   tweets = helpers.get_user_timeline(screen_name, 50)",      \
              " File \\"/root/helpers.py\\", line 45, in get_user_timeline", \
              "   raise RuntimeError(\\"API_KEY not set\\")",                \
              "RuntimeError: API_KEY not set",                               \
              "...",                                                         \
              "RuntimeError: API_SECRET not set"                             \
          ])[1][0]
      True

      >>> "already listening" in catch_all_python([        \
              "Traceback (most recent call last):",        \
              "OSError: [Errno 98] Address already in use" \
          ])[1][0]
      True
    """
    # check for recognized output
    if not re.search(r"^Traceback \(most recent call last\):$", lines[0]):
        return

    # iterate over lines ourselves
    for i, line in enumerate(lines):

        matches = re.search(r"^RuntimeError: (API_KEY|API_SECRET) not set$", line)
        if matches:
            response = [
                "`{}`, an environment variable, doesn't appear to be set, at least not in this " \
                    "tab".format(matches.group(1)),
                "Odds are you need to run `export {}=value`, where `value` is `{}`'s intended " \
                    "value.".format(matches.group(1), matches.group(1))
            ]

            return lines[i:i+1], response


        matches = re.search(r"^OSError: \[Errno 98\] Address already in use$", line)
        if matches:
            response = [
                "Another program is already listening on that port.",
                "Do you perhaps have this same command running in another tab?"
            ]

            return lines[i:i+1], response
