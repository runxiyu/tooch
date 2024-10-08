/* 
 * Help memorize Chinese poetry/prose
 *
 * Copyright (c) 2024 Runxi Yu <https://runxiyu.org>
 * SPDX-License-Identifier: BSD-2-Clause
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 * 
 *     1. Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 * 
 *     2. Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS "AS IS" AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

// FIXME: There's something wrong with the buffer length handling
//        I'm a bit sick so I don't want to figure out why right now
//        I should probably use libutf rather than wide characters anyway

#define _XOPEN_SOURCE_EXTENDED
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <wchar.h>
#include <ncurses.h>
#include <time.h>
#include <signal.h>
#include <locale.h>
#include <unistd.h>
#include <fcntl.h>

#define NORMAL 1
#define WRONG 2
#define CORRECT 3
#define BLANK 4
#define HALF 5
#define ACTIVE 6

const wchar_t PUNCTS[] = L"\uff1a\uff1b\u3002\uff01\uff1f\uff0c\u201c\u201d\u2018\u2019";	// ascii quotes don't appear in Chinese text
// const wchar_t PUNCTS[] = L",."; // why would you ever use this

void poof(int sig)
{
	endwin();
	exit(0);
}

void warn(const char *progname, const char *s)
{
	fprintf(stderr, "%s: %s\n", progname, s);
}

struct segment {
	wchar_t *text;
	bool display;
	wchar_t *ending_punctuation;
	int color;
};

void print_segments(struct segment *segments, int segment_count)
{
	int i;

	for (i = 0; i < segment_count; i++) {
		attron(COLOR_PAIR(segments[i].color));
		if (segments[i].display) {
			printw("%ls", segments[i].text);
		} else {
			printw("*");
		}
		attroff(COLOR_PAIR(segments[i].color));
		printw("%ls", segments[i].ending_punctuation);
	}
}

struct segment *parse_paragraph_to_segments(const wchar_t *t,
					    bool first_display,
					    int *segment_count)
{
	int len = wcslen(t);
	struct segment *segments;
	int i = 0, punct_idx = 0, text_idx = 0;
	bool current_display = first_display;
	wchar_t current_punctuation[10] = L"";
	wchar_t current_text[1000] = L"";

	if (len == 0)
		return NULL;

	segments = malloc(sizeof(*segments) * len);
	*segment_count = 0;

	for (;;) {
		if (wcschr(PUNCTS, t[i])) {
			current_punctuation[punct_idx++] = t[i++];
		} else if (punct_idx > 0) {
			current_punctuation[punct_idx] = L'\0';
			segments[*segment_count].text = wcsdup(current_text);
			segments[*segment_count].display = current_display;
			segments[*segment_count].ending_punctuation =
			    wcsdup(current_punctuation);
			segments[*segment_count].color =
			    current_display ? NORMAL : BLANK;
			(*segment_count)++;
			current_punctuation[0] = L'\0';
			punct_idx = 0;
			current_text[0] = L'\0';
			text_idx = 0;
			current_display = !current_display;
		} else {
			current_text[text_idx++] = t[i++];
		}

		if (i >= len) {	// FIXME
			current_text[text_idx] = L'\0';
			segments[*segment_count].text = wcsdup(current_text);
			segments[*segment_count].display = current_display;
			segments[*segment_count].ending_punctuation =
			    wcsdup(current_punctuation);
			segments[*segment_count].color =
			    current_display ? NORMAL : BLANK;
			(*segment_count)++;
			break;
		}
	}

	return segments;
}

int main(int argc, char *argv[])
{
	setlocale(LC_ALL, "");

	signal(SIGINT, poof);

	FILE *file;
	struct segment *segments = NULL;
	wchar_t line[1000];
	int segment_count = 0;
	int specified_line = -1;
	int current_line = 0;
	int i, n;
	int wrongs = 0;
	int corrects = 0;

	if (argc < 2) {
		warn(argv[0],
		     "Missing argument: Path to file to be memorized.");
		return 22;
	}

	file = fopen(argv[1], "r");
	if (!file) {
		warn(argv[0], "Cannot find file.");
		return 2;
	}

	if (argc > 2)
		specified_line = atoi(argv[2]) - 1;

	while (fgetws(line, sizeof(line) / sizeof(wchar_t), file)) {
		if (specified_line == -1 || current_line == specified_line) {
			line[wcscspn(line, L"\n")] = 0;
			if (wcslen(line) > 0) {
				struct segment *parsed_segments;
				int parsed_count;
				parsed_segments =
				    parse_paragraph_to_segments(line,
								rand() % 2,
								&parsed_count);
				segments =
				    realloc(segments,
					    sizeof(struct segment) *
					    (segment_count + parsed_count));
				for (i = 0; i < parsed_count; i++)
					segments[segment_count + i] =
					    parsed_segments[i];
				segment_count += parsed_count;
				free(parsed_segments);
			}
		}
		current_line++;
		if (specified_line != -1 && current_line > specified_line)
			break;
	}

	fclose(file);

	if (segment_count == 0) {
		warn(argv[0], "Empty segments list after parsing.");
		return 79;
	}

	if (segments[0].display) {
		if (segment_count > 1)
			segments[1].color = ACTIVE;
	} else {
		segments[0].color = ACTIVE;
	}

	initscr();
	start_color();
	init_pair(NORMAL, COLOR_WHITE, COLOR_BLACK);
	init_pair(WRONG, COLOR_RED, COLOR_BLACK);
	init_pair(CORRECT, COLOR_GREEN, COLOR_BLACK);
	init_pair(BLANK, COLOR_YELLOW, COLOR_BLACK);
	init_pair(HALF, COLOR_MAGENTA, COLOR_BLACK);
	init_pair(ACTIVE, COLOR_CYAN, COLOR_BLACK);

	cbreak();
	noecho();
	keypad(stdscr, TRUE);

	for (i = 0; i < segment_count; i++) {
		struct segment *segment = &segments[i];
		wchar_t got[1000];

		clear();
		print_segments(segments, segment_count);
		printw("\n\n");
		refresh();

		if (!segment->display) {
			mvprintw(LINES - 2, 0, "* ");
			echo();
			getn_wstr(got, sizeof(got) - 1);
			noecho();

			if (wcscmp(got, segment->text) == 0) {
				segment->display = true;
				segment->color = CORRECT;
				corrects++;
			} else if (wcslen(got) == 0) {
				segment->display = true;
				segment->color = WRONG;
				wrongs++;
			} else {
				mvprintw(LINES - 2, 0, "Retry: ");
				echo();
				getnstr((char *)got, sizeof(got) - 1);
				noecho();

				if (wcscmp(got, segment->text) == 0) {
					segment->display = true;
					segment->color = CORRECT;
					corrects++;
				} else {
					segment->display = true;
					segment->color = WRONG;
					wrongs++;
				}
			}

			n = i;
			while (n < segment_count && segments[n].display)
				n++;
			if (n < segment_count)
				segments[n].color = ACTIVE;
		}
	}

	clear();
	print_segments(segments, segment_count);
	printw("\n\n");
	printw("Summary:\n\tCorrect: %d\n\tIncorrect: %d\n", corrects, wrongs);
	refresh();

	getch();
	endwin();

	for (int i = 0; i < segment_count; i++) {
		free(segments[i].text);
		free(segments[i].ending_punctuation);
	}
	free(segments);
	// Yes, the OS will free things, but I'm kinda convinced that this is
	// good practice anyways, and there's about no harm.

	return 0;
}
