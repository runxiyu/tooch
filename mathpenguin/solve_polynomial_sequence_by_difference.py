#!/usr/bin/env python3

# program unfinished and broken

from fractions import Fraction
from numpy import array, array_equal
import numpy
import sys

from pprint import pprint


def error(s):
    print(s, file=sys.stderr)
    exit(1)


def all_items_are_equal(l):
    o = l[0]
    for i in l[1:]:
        if type(o) is numpy.ndarray:
            if not array_equal(o, i):
                return False
        elif o != i:
            return False
    return True


def differentiate_between_adjacent_items(l):
    return [(l[i + 1] - l[i]) for i in range(len(l) - 1)]


def layers(l):
    if all_items_are_equal(l):
        return [l]
    return [l] + layers(differentiate_between_adjacent_items(l))


def degree_general_form(f):
    def _(n):
        return array(list([n**e for e in range(f + 1)]))

    return _


def degree_layers(d):
    return layers([degree_general_form(d)(n) for n in range(1, d + 3)])


def solve(o):
    l = layers(o)
    if len(l[-1]) < 2:  # set to 1 to be loose but possibly inaccurate
        raise ValueError("Not enough samples or not polynomial")
    assert all_items_are_equal(l[-1])
    deg = len(l) - 1
    degl = degree_layers(deg)
    coefficients = [None] * (deg + 1)
    # coefficients[deg] = Fraction(degl[deg][0][-1], l[deg][-1])
    coefficients[deg] = Fraction(l[deg][0], degl[deg][0][deg])
    pprint(("l", l))
    pprint(("degl", degl))
    for i in reversed(list(range(deg))):
        print()
        print(i)
        coefficients[i] = l[i][0] - sum(
            [(coefficients[ix] * (degl[i][0][ix])) for ix in range(i + 1, deg + 1)]
        )
        pprint(("coef", coefficients))
        # print(l[i] - degl[i]coefficients[i + 1])
        # print(l[i][0] - sum([coefficients[d] for d in range(i - 1, deg 1)]))
    #         print(i)
    #         print(degl[i])
    #         print(l[i][0])

    print("---")
    return coefficients


def main():
    istr = input(
        "Enter a polynomial sequence for me to identify.\nExample: 1 4 9 16 25 36\n> "
    )
    try:
        its = [Fraction(i) for i in istr.split(" ") if i]
    except ValueError:
        error("You need to give me numbers, not some jibberish.")
    if len(its) < 3:
        error(
            "You need to give me at least three items to meaningfully identify a sequence."
        )
    print("Process:")
    print(" ".join([str(i) for i in its]))
    if all_items_are_equal(its):
        print(its[0])
        exit(0)
    pts = []
    for i in range(len(its) - 1):
        pts.append(its[i + 1] - its[i])
    print(" ".join([str(i) for i in pts]))
    if len(pts) > 1 and all_items_are_equal(pts):
        print("\nResults:")
        print(str(its[0] - pts[0]) + " + " + str(pts[0]) + "n")
        exit(0)
    elif len(pts) == 1:
        error(
            "I don't have enough samples to solve the sequence, or maybe the sequence diverges."
        )
    rts = []
    for i in range(len(pts) - 1):
        rts.append(pts[i + 1] - pts[i])
    print(" ".join([str(i) for i in rts]))
    if len(rts) > 1 and all_items_are_equal(rts):
        print("\nResults:")
        second_degree_coefficient = Fraction(rts[0], 2)
        first_degree
        print(
            str(its[0] - pts[0])
            + " + "
            + str(pts[0] - Fraction(3, 2) * Fraction(rts[0], 2))
            + "n + "
            + str(Fraction(rts[0], 2))
            + "n^2"
        )
        exit(0)
    elif len(pts) == 1:
        error(
            "I don't have enough samples to solve the sequence, or maybe the sequence diverges."
        )


if __name__ == "__main__":
    main()
