#!/usr/bin/env python3

import sys


def error(s):
    print(s, file=sys.stderr)
    exit(1)


def all_items_are_equal(l):
    o = l[0]
    for i in l[1:]:
        if o != i:
            return False
    return True


def differentiate_between_adjacent_items(l):
    return [(l[i + 1] - l[i]) for i in range(len(l) - 1)]


def layers(l):
    if all_items_are_equal(l):
        return [l]
    return [l] + layers(differentiate_between_adjacent_items(l))


def solve(o):
    l = layers(o)
    if len(l[-1]) < 1:
        raise ValueError("Not enough samples or invalid.")
    elif len(l[-1]) == 1:
        print("Warning: Only one sample for the last layer, likely wrong!")
    assert all_items_are_equal(l[-1])

    max_degree = len(l) - 1

    if max_degree == 0:
        return [l[0][0]]
    elif max_degree == 1:
        return [l[0][0] - l[1][0], l[1][0]]
    elif max_degree == 2:
        return [
            l[0][0] - (l[1][0] - 3 * (l[2][0] / 2)) - (l[2][0] / 2),
            l[1][0] - 3 * (l[2][0] / 2),
            (l[2][0] / 2),
        ]
    elif max_degree == 3:
        return [
            l[0][0] - (l[1][0] - 3 * ((l[2][0] - (2 * l[3][0])) / 2) - 7 * (l[3][0] / 6)) - ((l[2][0] - (2 * l[3][0])) / 2) - (l[3][0] / 6),
            l[1][0] - 3 * ((l[2][0] - (2 * l[3][0])) / 2) - 7 * (l[3][0] / 6),
            (((l[2][0] - (2 * l[3][0]))) / 2),
            (l[3][0] / 6),
        ]
    else:
        raise ValueError("Can't solve %d-degree." % max_degree)



def main():
    istr = input("Enter a polynomial sequence for me to identify: ")
    try:
        its = [float(i) for i in istr.split(" ") if i]
    except ValueError:
        error("You need to give me numbers, not some jibberish.")
    if len(its) < 3:
        error(
            "You need to give me at least three items to meaningfully identify a sequence."
        )
    try:
        sl = solve(its)
        pr = []
        for d in range(len(sl)):
            if str(sl[d]) != "0":
                if d in (2, 3):
                    pr.append("%s n^%d" % (str(sl[d]), d))
                elif d == 1:
                    pr.append("%s n" % (str(sl[d])))
                elif d == 0:
                    pr.append("%s" % (str(sl[d])))
        pr.reverse()  # in-place
        print("U_n = %s" % ' + '.join(pr))
    except ValueError as e:
        error(e)


if __name__ == "__main__":
    main()

