# -*- encoding: utf-8 -*-

import argparse
import os
from os.path import join, getsize
import locale

total_total = 0
locale.setlocale(locale.LC_ALL, '')


def main():
    parser = argparse.ArgumentParser(
        description='Display sizes of the current subdirectories.'
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Increase output verbosity",
        type=int,
        choices=[-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        default=0,
    )
    args = parser.parse_args()
    verbose = args.verbose

    msg = "T %12s %s %s" % (
        locale.format("%d", get_total_size('.'), grouping=True),
        '',
        '.'
    )
    print msg
    rec_tree_traverse('.', 0, verbose)


def get_total_size(path):
    total = 0
    for root, dirs, files in os.walk(path):
        subtotal = (sum(getsize(join(root, name)) for name in files))
        total += subtotal
        #print("bytes in", root, subtotal)
    return total


def rec_tree_traverse(curr_dir, indent, verbose):
    "recursive function to traverse the directory"
    files_subtotal = 0
    try:
        dfList = [
            os.path.join(curr_dir, f_or_d) for f_or_d in os.listdir(curr_dir)
        ]
    except:
        print "wrong path name/directory name"
        return

    for file_or_dir in dfList:
        if os.path.isfile(file_or_dir):
            files_subtotal += getsize(file_or_dir)
            if verbose == -1:
                msg = "  %12s %s %s" % (
                    locale.format("%d", getsize(file_or_dir), grouping=True),
                    ' ' * indent,
                    file_or_dir
                )
                print msg

    if verbose == -1:
        msg = "  %12s %s %s" % (
            locale.format("%d", files_subtotal, grouping=True),
            ' ' * indent,
            curr_dir
        )
        print msg

    for file_or_dir in dfList:
        if os.path.isdir(file_or_dir):
            msg = "D %12s %s %s" % (
                locale.format("%d",
                    get_total_size(file_or_dir), grouping=True),
                ' ' * indent,
                file_or_dir
            )
            print msg
            if verbose < 0 or indent < verbose:
                rec_tree_traverse(file_or_dir, indent + 2, verbose)
