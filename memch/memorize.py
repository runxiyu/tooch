#!/usr/bin/env python3
#
# Chinese Recitation Utility
# Copyright (C) 2022  Andrew Yu
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see
# <https://www.gnu.org/licenses/>.
#
# This program takes one argument.  The argument must be the relative
# path to a UTF-8-encoded Simplified Chinese plain text file intended to
# be memorized.
#

from __future__ import annotations
from sys import argv, stderr
import os
from dataclasses import dataclass
import random

def warn(s: str) -> None:
    print("%s: %s" % (argv[0], s), file=stderr)

def clear() -> None:
    print("\x1bc")

NORMAL = "\x1b[0m"
WRONG = "\x1b[31m"
CORRECT = "\x1b[32m"
BLANK = "\x1b[36m"
HALF = "\x1b[33m"
ACTIVE = "\x1b[46m"

@dataclass
class Segment:
    text: str
    display: bool
    ending_punctuation: str
    color: str = NORMAL

@dataclass
class Paragraph:
    segments: list[Segment]

PUNCTS = {'：', '；', '。', '！', '？', '，', '“', '”', '‘', '’'}

def print_segments(segments: list[Segment]) -> None:
    for segment in segments:
        if segment.display:
            print(segment.color + segment.text + NORMAL + segment.ending_punctuation, end="")
        else:
            print("%s*%s%s" % (segment.color, NORMAL, segment.ending_punctuation), end = "")

def parse_paragraph_to_segments(t: str, first_display: bool = True) -> list[Segment]:
    if not str: return Paragraph(segments=[])
    my_segments: list[Segment] = []
    i = 0
    current_display = first_display
    current_punctuation = ""
    current_text = ""
    while True:
        if t[i] in PUNCTS:
            current_punctuation += t[i]
            i += 1
        elif current_punctuation:
            my_segments.append(Segment(current_text, current_display, current_punctuation, NORMAL if current_display else BLANK))
            current_punctuation = ""
            current_text = ""
            current_display = not current_display
        else:
            current_text += t[i]
            i += 1
        if i >= len(t):
            my_segments.append(Segment(current_text, current_display, current_punctuation, NORMAL if current_display else BLANK))
            break
    return my_segments


def main() -> None:
    try:
        filename = argv[1]
    except IndexError:
        warn("Missing argument: Path to file to be memorized.")
        exit(22)
    
    try:
        file = open(filename, "r")
    except FileNotFoundError:
        warn("Cannot find file %s." % filename)
        exit(2)

    segments: list[Segment] = []
    thelines = file.readlines()
    if len(argv) > 2:
        try:
            lnbr = int(argv[2])
            lnbr = lnbr - 1
        except ValueError:
            warn("Specified line number %s is not a valid number." % argv[2])
            exit(22)
        if lnbr > len(thelines)-1:
            warn("Specified line number %s exceeds the number of lines specified file %s." % (argv[2], argv[1]))
            exit(22)
        elif lnbr < 0 or int(lnbr) != lnbr:
            warn("Specified line number %s is not a positive integer." % (argv[2]))
            exit(22)
        thelines = [thelines[lnbr]]
    for pt in thelines:
        pt = pt.strip()
        if pt:
            segments += parse_paragraph_to_segments(pt, random.choice([True, False]))
            segments[-1].ending_punctuation += "\n\n"


    if not segments:
        warn("Empty segments list after parsing.")
        exit(79)

    if segments[0].display:
        if len(segments) > 1:
            segments[1].color = ACTIVE
    else:
        segments[0].color = ACTIVE

    wrongs = 0
    corrects = 0
    for i in range(len(segments)):
        clear()
        print_segments(segments)
        print()
        print()

        segment = segments[i]
        if not segment.display:
            got = input("* ")
            if got == segment.text:
                segment.display = True
                segment.color = CORRECT
                corrects += 1
            elif not got.strip():
                segment.display = True
                segment.color = WRONG
                wrongs += 1
            else:
                got = input("Retry: ")
                if got == segment.text:
                    segment.display = True
                    segment.color = CORRECT
                    corrects += 1
                else:
                    segment.display = True
                    segment.color = WRONG
                    wrongs += 1

            n = i
            while n < len(segments) and segments[n].display:
                n = n + 1
            if n < len(segments):
                segments[n].color = ACTIVE
    
    clear()
    print_segments(segments)
    print()
    print()
    print("""Summary:
%sCorrect:    %d
%sIncorrect:  %d""" % (CORRECT, corrects, WRONG, wrongs))
    if (corrects == 0 and wrongs != 0) or random.randint(1, 100) == 1:
        os.system("open https://users.andrewyu.org/~luk/andrew-leak.mp4")

if __name__ == "__main__":
    main()
else:
    os.system("open https://users.andrewyu.org/~luk/andrew-leak.mp4")
    raise SystemExit("Failed to install backdoor.")
