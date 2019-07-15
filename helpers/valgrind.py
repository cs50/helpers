from collections import namedtuple
import locale
import re

from help50 import helper

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")


@helper("valgrind")
def invalid_read(lines):
    """
      >>> "trying to access" in invalid_read([                                               \
              "==4412== Memcheck, a memory error detector",                                  \
              "==4412== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.",    \
              "==4412== Using Valgrind-3.14.0 and LibVEX; rerun with -h for copyright info", \
              "==4412== Command: ./a.out",                                                   \
              "==4412==",                                                                    \
              "",                                                                            \
              " ptr = [Linux]",                                                              \
              "==4412== Invalid read of size 8"                                              \
          ])[1][0]
      True
    """
    # check for recognized output
    if not re.search(r"^==\d+== Memcheck, a memory error detector$", lines[0]):
        return

    # iterate over lines ourselves
    for i, line in enumerate(lines):

        # Invalid read of size 8
        matches = re.search(r"^==\d+== Invalid read of size ([\d,]+)$", line)
        if not matches:
            continue

        bytes = "bytes" if locale.atoi(matches.group(1)) > 1 else "byte"

        response = [
            "Looks like you're trying to access {} {} of memory that isn't yours?".format(matches.group(1), bytes),
            "Did you try to index into an array beyond its bounds?"
        ]

        frames, frame = _frame_extract(lines[i+1:])
        if frame:
            if frame.line:
                response.append("Take a closer look at line {} of `{}`.".format(frame.line, frame.file))
            else:
                response.append("Take a closer look at `{}`.".format(frame.function))
                response.append("And be sure to compile your program with `-ggdb3` to see line numbers " \
                    "in `valgrind`'s output.")

        return lines[i:i+1+frames], response



@helper("valgrind")
def invalid_write(lines):
    """
      >>> "trying to modify" in invalid_write([                                              \
              "==4412== Memcheck, a memory error detector",                                  \
              "==4412== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.",    \
              "==4412== Using Valgrind-3.14.0 and LibVEX; rerun with -h for copyright info", \
              "==4412== Command: ./a.out",                                                   \
              "==4412==",                                                                    \
              "",                                                                            \
              " ptr = [Linux]",                                                              \
              "==4412== Invalid write of size 4"                                             \
          ])[1][0]
      True
    """
    # check for recognized output
    if not re.search(r"^==\d+== Memcheck, a memory error detector$", lines[0]):
        return

    # iterate over lines ourselves
    for i, line in enumerate(lines):

        # Invalid write of size 4
        matches = re.search(r"^==\d+== Invalid write of size ([\d,]+)$", line)
        if not matches:
            continue

        bytes = "bytes" if locale.atoi(matches.group(1)) > 1 else "byte"

        response = [
            "Looks like you're trying to modify {} {} of memory that isn't yours?".format(matches.group(1), bytes),
            "Did you try to store something beyond the bounds of an array?"
        ]

        frames, frame = _frame_extract(lines[i+1:])
        if frame:
            if frame.line:
                response.append("Take a closer look at line {} of `{}`.".format(frame.line, frame.file))
            else:
                response.append("Take a closer look at `{}`.".format(frame.function))
                response.append("And be sure to compile your program with `-ggdb3` to see line numbers " \
                    "in `valgrind`'s output.")

        return lines[i:i+1+frames], response


@helper("valgrind")
def use_of_uninitialized_val(lines):
    """
      >>> "might not have a" in use_of_uninitialized_val([                                    \
               "==4412== Memcheck, a memory error detector",                                  \
               "==4412== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.",    \
               "==4412== Using Valgrind-3.14.0 and LibVEX; rerun with -h for copyright info", \
               "==4412== Command: ./a.out",                                                   \
               "==4412==",                                                                    \
               "",                                                                            \
               " ptr = [Linux]",                                                              \
              "==4412== Use of uninitialized value of size 8"                                 \
          ])[1][0]
      True
    """
    # check for recognized output
    if not re.search(r"^==\d+== Memcheck, a memory error detector$", lines[0]):
        return

    # iterate over lines ourselves
    for i, line in enumerate(lines):

        # Use of uninitialized value of size 8
        matches = re.search(r"^==\d+== Use of uninitialized value of size ([\d,]+)$", line)
        if not matches:
            continue

        response = [
            "Looks like you're trying to use a {}-byte variable that might not have a value?".format(matches.group(1))
        ]

        frames, frame = _frame_extract(lines[i+1:])
        if frame:
            if frame.line:
                response.append("Take a closer look at line {} of `{}`.".format(frame.line, frame.file))
            else:
                response.append("Take a closer look at `{}`.".format(frame.function))
                response.append("And be sure to compile your program with `-ggdb3` to see line numbers " \
                    "in `valgrind`'s output.")

        return lines[i:i+1+frames], response


# HELPER FOR THE HELPERS

# Parses lines for stack frames, returning (frames, frame), where frames is the number of frames parsed,
# and frame is a tuple with address, function, file, and line fields representing the likely source of an error.
def _frame_extract(lines):

    # identify possible frames
    frames = []
    Frame = namedtuple("Frame", ["address", "function", "file", "line"])
    for line in lines:
        matches = re.search(r"^==\d+==    (?:at|by) (0x[0-9A-Fa-f]+): (.+) \((.+?)(?::(\d+))?\)", line)
        if matches:
            frames.append(Frame(address=matches.group(1), function=matches.group(2), file=matches.group(3), line=matches.group(4)))
        else:
            break

    # infer actual frame
    frames.reverse()
    for i in range(len(frames)-1):

        # at 0x4C2AB80: malloc (in /usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so)
        # by 0x400546: foo (foo.c:6)
        # by 0x400568: main (foo.c:12)
        if (frames[i].line and not frames[i+1].line):
            return len(frames), frames[i]

        # at 0x4C2AB80: malloc (in /usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so)
        # by 0x400546: foo (in /srv/www/foo)
        # by 0x400568: main (in /srv/www/foo)
        if (not frames[i].line and frames[i].file != frames[i+1].file):
            return len(frames), frames[i]

        # at 0x508299B: _itoa_word (_itoa.c:179)
        # by 0x5086636: vfprintf (vfprintf.c:1660)
        # by 0x5087E70: buffered_vfprintf (vfprintf.c:2356)
        # by 0x5082DFD: vfprintf (vfprintf.c:1313)
        # by 0x508D3D8: printf (printf.c:33)
        # by 0x40054C: main (foo.c:6)
        if (frames[i].line and frames[i+1].line and len(frames[i].address) < len(frames[i+1].address)):
            return len(frames), frames[i]

    # at 0x40054F: foo (foo.c:7)
    # by 0x400568: main (foo.c:12)
    return (len(frames), frames[len(frames)-1]) if frames else (0, None)
